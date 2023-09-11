# Offline E-Logbook

## Warning: WIP

This is in a very early stage, don't use it just yet. **It might corrupt your log book entries**.

A detailed documentation will be available soon ...

## Introduction

The purpose of this app is to cache the log book entries locally to quickly display them and search
in them.

Theoretically this could be used as fully functional logbook client, since uploading new events
(and modifying existing ones) is well within the capabilities of the API.

## Usage

From a place in the technical network, start the logbook with

```shell
python logbook.py
```

In order to download new entries, click on `File->'Retrieve Elements'`. 

Note: right now the progress pop-up doesn't work (it stays black, might be some interference with
the downloading process, which runs on another thread)
