# BoostFace pyqt6

## Introduction

- desktop application for BoostFace, which is a face recognition system based BoostFace on front-end and back-end with
  fastapi cloud compute
- the front-end is based on pyqt6 and the back-end is based on fastapi
- the database is based on supabase and milvus in fastapi cloud compute

## Project Architecture
- layout
    - home UI✅
        - total state
        - camera
        - access record
    - setting UI✅
        - camera setting
        - basic setting...
    - local-dev-info UI✅
        - desktop app console logs
        - camera info
        - desktop system monitor
    - cloud-dev-info UI✅
        - cloud app console logs
        - cloud info
        - cloud system monitor

## Project Process🌈
1. basic layout by pyqt6 ✅
    1. main_window
    2. home_ui
    3. setting_ui
    4. local_dev_info_ui
    5. cloud_dev_info_ui
2. how to config?
3. fastapi client?
    1. login? ->✅
    2. connect to cloud?
4. boostface integration local and connect to cloud?
