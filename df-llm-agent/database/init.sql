-- DROP DATABASE IF EXISTS deepflow_llm;

-- CREATE DATABASE deepflow_llm;

-- USE deepflow_llm;

CREATE TABLE IF NOT EXISTS db_version (
    id                  INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
	`version`           CHAR(64) NOT NULL DEFAULT '',
	created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at          DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)ENGINE=innodb DEFAULT CHARSET=utf8 COMMENT='db版本';
TRUNCATE TABLE db_version;

CREATE TABLE IF NOT EXISTS chat_topic(
    id                  INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id             INTEGER NOT NULL DEFAULT 0,
    `name`              VARCHAR(256) NOT NULL DEFAULT '' COMMENT '对话主题标题',
    `type`              TINYINT(1) NOT NULL DEFAULT 0 COMMENT '对话主题类型',
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `user_id` (`user_id`)
)ENGINE=innodb DEFAULT CHARSET=utf8 COMMENT='对话主题';
TRUNCATE TABLE  chat_topic;


CREATE TABLE IF NOT EXISTS chat(
    id                  INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
    chat_topic_id       INTEGER NOT NULL DEFAULT 0 COMMENT '主题id, 一个主题包含多个对话',
    `input`             LONGTEXT COMMENT '会话问题',
    `output`            LONGTEXT COMMENT 'llm返回的数据经过提取后用于显示的内容',
    `output_all`        json COMMENT 'llm返回的原生数据或请求异常信息',
    `engine`            VARCHAR(64) NOT NULL DEFAULT '' COMMENT '对话用的llm引擎',
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `chat_topic_id` (`chat_topic_id`)
)ENGINE=innodb DEFAULT CHARSET=utf8 COMMENT='对话';
TRUNCATE TABLE  chat;


CREATE TABLE IF NOT EXISTS score(
    id                  INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id             INTEGER NOT NULL DEFAULT 0,
    `type`              TINYINT(1) NOT NULL DEFAULT 0 COMMENT '1: 主题评分,2: 对话评分',
    obj_id              INTEGER NOT NULL DEFAULT 0 COMMENT '主题id或对话id',
    score               TINYINT(1) NOT NULL DEFAULT 0 COMMENT '评分0-100',
    feedback            TEXT COMMENT '反馈信息',
    user_name           VARCHAR(64) COMMENT '反馈者',
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `user_id` (`user_id`)
)ENGINE=innodb DEFAULT CHARSET=utf8 COMMENT='评分';
TRUNCATE TABLE  score;