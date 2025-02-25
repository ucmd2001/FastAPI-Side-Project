# Web's Project

```
├─ .pytest_cache
│  ├─ CACHEDIR.TAG
│  ├─ README.md
│  └─ v
│     └─ cache
│        ├─ lastfailed
│        ├─ nodeids
│        └─ stepwise
├─ apps
│  ├─ plan_cart
│  │  ├─ api.py
│  │  ├─ schema.py
│  │  ├─ service.py
│  ├─ routers.py
├─ configs
│  ├─ database.py
│  ├─ settings.py
├─ database
│  └─ sqlite3.db
├─ local.env
├─ main.py
├─ model
│  ├─ crud.py
│  ├─ model.py
├─ README.md
├─ requirements.txt
└─ tests
   ├─ database
   │  ├─ test_database.py
   └─ plan_cart
      ├─ test_plan_cart.py
      ├─ test_plan_cart_api.py
```

# 使用技術:
後端: FastAPI

DB: sqlite3

# 安裝必要套件 (需先安裝Python)
1. 輸入 pip install -r requirements.txt
2. 會自動開始安裝必要套件

# 啟動專案方式:
1. 啟動終端機
2. 輸入 python main.py
3. 開啟網頁瀏覽器
4. 輸入 127.0.0.1:8000/docs
5. 即可開始使用系統

# 單元測試執行方式
1. 啟動終端機
2. 輸入 pytest tests/
3. 即可開始測試
