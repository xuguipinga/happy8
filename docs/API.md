# API 接口文档

系统提供了一套完整的 RESTful API 供前端或第三方应用调用。

## 1. 获取综合数据
- **URL**: `/api/data`
- **Method**: `GET`
- **Query Parameters**:
  - `limit` (optional): 返回的数据期数，默认 50。
- **Response**: 返回历史记录、统计分析和模式分析结果。

## 2. 强制刷新
- **URL**: `/api/refresh`
- **Method**: `GET`
- **Query Parameters**:
  - `num` (optional): 获取的数量，默认 50。
- **Response**: 获取最新开奖数据并重新计算分析。

## 3. 推荐历史
- **URL**: `/api/history`
- **Method**: `GET`
- **Response**: 返回历史各期系统给出的推荐号码及其实际中奖验证情况。

## 4. 录入新数据
- **URL**: `/api/submit_data`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "period": "2024001",
    "numbers": ["01", "05", ..., "80"]
  }
  ```
- **Response**: 成功或失败的状态。

## 5. 健康检查
- **URL**: `/health`
- **Method**: `GET`
- **Response**: `{"status": "healthy", "timestamp": "..."}`
