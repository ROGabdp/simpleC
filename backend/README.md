# CFD 求解器後端

## 安裝

```bash
cd backend
pip install -r requirements.txt
```

## 執行

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 開發

### 執行測試

```bash
pytest tests/
```

### 程式碼格式化

```bash
black app/ tests/
```

### Linting

```bash
flake8 app/ tests/
mypy app/
```

## API 文檔

啟動後端後,訪問:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
