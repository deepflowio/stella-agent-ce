#
服务启动，判断是否存在数据库
- 不存在(全新部署)
    - 创建库和表，创建表失败就回滚并删除库
- 存在（db_version表肯定存在）
  - 判断issu中版本，只执行大于version版本的issu

db_version 初始版本为1.0.0.0，每次更新issu，都依次递增例如：1.0.0.1, 1.0.0.2

每次新增x.x.x.x.sql时 都必须同时更新dockerfile里的db_version

