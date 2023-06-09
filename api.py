from typing import *
import pylogbook
from pylogbook.models import Event, PaginatedEvents
import mimetypes
from requests.exceptions import ConnectTimeout, ConnectionError, HTTPError
from pathlib import Path
import json
from datetime import date, datetime, timedelta
import urllib3

from rbac import RBAC
from events import DATETIMEFORMAT, DATEFORMAT

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Possible errors during RBAC connection
CONNECTION_ERRORS = (HTTPError, ConnectionError, ConnectTimeout, ImportError, RuntimeError)

OMC_LOGBOOK = "LHC_OMC"
PNG_DPI = 300  # dpi for converted png (from pdf)


# for typing:
try:
    from pylogbook._attachment_builder import AttachmentBuilder, AttachmentBuilderType
    from pylogbook.models import Event
except ImportError:
    AttachmentBuilderType, Event = type(None), type(None)
    AttachmentBuilder = None

class EventDownloader:
    def __init__(self,
                 from_date: datetime = datetime.now() + timedelta(weeks=-5),
                 to_date: datetime = datetime.now()) -> None:
        rbac_token = _get_rbac_token()
        self.client = pylogbook.Client(rbac_token=rbac_token)
        self.logbook = pylogbook.ActivitiesClient(OMC_LOGBOOK, client=self.client)
        self.events = self.logbook.get_events(from_date=from_date, to_date=to_date)
        self.page_number: int = 0

        print(f"npages: {self.events.n_pages()}")

    def __iter__(self):
        return self

    def __next__(self) -> int:
        print("next")
        if self.page_number == self.events.n_pages():
            print("end iteration")
            raise StopIteration
        current_page = self.events.get_page(self.page_number)
        self.page_number += 1
        print(f"page: {self.page_number}")

        for p in current_page:
            with open(f"{p.event_id}.json", "w") as ofile:
                jsonevent = {}
                jsonevent["comment"] = p.comment
                jsonevent["date"] = p.date.strftime(DATETIMEFORMAT)
                jsonevent["id"] = p.event_id

                jsonattachements = []
                for jatt in p.attachments:
                    url = self.client._service_client._server_url + jatt._extra["urlToContent"]
                    resp = self.client._service_client._make_authd_request("get", url)
                    orig_filename = Path(jatt.filename)
                    filename = Path(str(jatt.attachment_id)).with_suffix(orig_filename.suffix)
                    with open(filename, "wb") as att_file:
                        att_file.write(resp.content)

                    jsonattachements.append( {
                        "id": jatt.attachment_id,
                        "url": url,
                        "creator": jatt.creator,
                        "filename": str(filename),
                    })


                jsonevent["attachments"] = jsonattachements
                ofile.write(json.dumps(jsonevent))
        return int( 100 * float(self.page_number) / float(self.events.n_pages()))

        



def retrieve_events(from_date: datetime = datetime.now() + timedelta(weeks=5),
                    to_date: datetime = datetime.now()):

    print(events)
    print(f"{events.count}")
    print(f"n pages: {events.n_pages()}")

    for n in range(events.n_pages()):
        print(f"--- page {n}")
        page_n = events.get_page(n)
        print("retrieved page from API")

        for p in page_n:
            print(f"    event {p.event_id} {p.date.strftime(DATETIMEFORMAT)}")
            with open(f"{p.event_id}.json", "w") as ofile:
                jsonevent = {}
                jsonevent["comment"] = p.comment
                jsonevent["date"] = p.date.strftime(DATETIMEFORMAT)
                jsonevent["id"] = p.event_id

                jsonattachements = []
                for jatt in p.attachments:
                    url = client._service_client._server_url + jatt._extra["urlToContent"]
                    resp = client._service_client._make_authd_request("get", url)
                    orig_filename = Path(jatt.filename)
                    filename = Path(str(jatt.attachment_id)).with_suffix(orig_filename.suffix)
                    with open(filename, "wb") as att_file:
                        att_file.write(resp.content)

                    jsonattachements.append( {
                        "id": jatt.attachment_id,
                        "url": url,
                        "creator": jatt.creator,
                        "filename": str(filename),
                    })


                jsonevent["attachments"] = jsonattachements
                ofile.write(json.dumps(jsonevent))

def _get_rbac_token() -> str:
    """ Get an RBAC token, either by location or by Kerberos. """
    rbac = RBAC(application=f"omc3.{Path(__file__).stem}")
    try:
        rbac.authenticate_location()
    except CONNECTION_ERRORS as e:
        print(
            f"Getting RBAC token from location failed. "
            f"{e.__class__.__name__}: {str(e)}"
        )
    else:
        print(f"Logged in to RBAC via location as user {rbac.user}.")
        return rbac.token

    try:
        rbac.authenticate_kerberos()
    except CONNECTION_ERRORS as e:
        print(
            f"Getting RBAC token via Kerberos failed. "
            f"{e.__class__.__name__}: {str(e)}"
        )
    else:
        print(f"Logged in to RBAC via Kerberos as user {rbac.user}.")
        return rbac.token

    # DEBUG ONLY ---
    # try:
    #     rbac.authenticate_explicit(user=input("Username: "), password=input("Password: "))
    # except CONNTECTION_ERRORS as e:
    #     print(
    #         f"Explicit RBAC failed. "
    #         f"{e.__class__.__name__}: {str(e)}"
    #     )
    # else:
    #     print(f"Logged in to RBAC as user {rbac.user}.")
    #     return rbac.token

    raise NameError("Could not get RBAC token.")

# Private Functions ------------------------------------------------------------


def _get_attachments(files: Iterable[Union[str, Path]],
                     filenames: Iterable[str] = None,
                     pdf2png: bool = False) -> List[AttachmentBuilderType]:
    """ Read the file-attachments and assign their names. """
    if files is None:
        return []

    if filenames and len(filenames) != len(files):
        raise ValueError(
            f"List of files (length {len(files)}) and "
            f"list of filenames (length: {filenames}) "
            f"need to be of equal length."
        )

    _add_mimetypes(files)
    if filenames is None:
        filenames = [None] * len(files)

    # TODO: Return iterator, reading attachments only when needed?
    attachments = []
    for filepath, filename in zip(files, filenames):
        filepath = Path(filepath)
        attachment = AttachmentBuilder.from_file(filepath)
        attachments.append(attachment)

        # Convert pdf to png if desired
        png_attachment = None
        if pdf2png and filepath.suffix.lower() == ".pdf":
            png_attachment = _convert_pdf_to_png(filepath)

        if png_attachment:
            attachments.append(png_attachment)

        # Assign new filenames
        if filename and filename.lower() != "none":
            attachment.short_name = filename
            if png_attachment:
                png_attachment.short_name = filename.replace(".pdf", ".png").replace(".PDF", ".png")

    return attachments


def _add_mimetypes(files: Iterable[Union[str, Path]]):
    """ Adds all unknown suffixes as plain/text, which should suffice for our
    purposes.
    TODO: if it's a binary sdds file, it should be 'application/octet-stream'
          see https://stackoverflow.com/a/6783972/5609590

    This is done, because the attachment builder uses the mimetypes package
    to guess the mimetype and if it doesn't find it (e.g. `.tfs` or `.dat`)
    raises an error.
    """
    if files is None:
        return

    for f in files:
        f_path = Path(f)
        mime, _ = mimetypes.guess_type(f_path.name)
        if mime is None:
            mimetypes.add_type("text/plain", f.suffix, strict=True)


def _convert_pdf_to_png(filepath: Path):
    """ Convert the first page of a pdf file into a png image. """
    try:
        import fitz  # PyMuPDF, imported as fitz for backward compatibility reasons
    except ImportError:
        print("Missing `pymupdf` package. PDF conversion not possible.")
        return None

    doc = fitz.open(filepath)  # open document

    if len(doc) > 1:
        print(f"Big PDF-File with {len(doc)} pages found. "
                       "Conversion only implemented for single-page files. "
                       "Skipping conversion.")
        return None

    pixmap = doc[0].get_pixmap(dpi=PNG_DPI)  # only first page
    attachment = AttachmentBuilder.from_bytes(
        contents=pixmap.tobytes("png"),
        mime_type="image/png",
        name=filepath.with_suffix(".png").name
    )
    return attachment

