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


CREATE TABLE IF NOT EXISTS llm_config(
    id                  INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id             INTEGER NOT NULL DEFAULT 0,
    `platform`          VARCHAR(64) NOT NULL DEFAULT '' COMMENT '平台: azure、aliyun、baidu、tencent',
    `model`            VARCHAR(64) NOT NULL DEFAULT '' COMMENT '模型统称,例如 azure: openai, 阿里: dashscope, 百度: qianfan, 腾讯: hyllm',
    `model_info`       VARCHAR(255) NOT NULL DEFAULT '' COMMENT '模型相关具体细节',
    `key`               VARCHAR(64) NOT NULL DEFAULT '' COMMENT '模型需要的配置项',
    `value`             VARCHAR(256) NOT NULL DEFAULT '' COMMENT '模型需要的配置项的值',
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `user_id` (`user_id`),
    UNIQUE KEY `unique_engine` (`user_id`,`platform`,`model`,`key`,`value`)
)ENGINE=innodb DEFAULT CHARSET=utf8 COMMENT='llm 配置';
TRUNCATE TABLE  llm_config;

INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'azure','gpt','enable',0);
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'azure','gpt','api_key','');
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'azure','gpt','api_type','azure');
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'azure','gpt','api_base','');
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'azure','gpt','api_version','');
-- INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'azure','gpt','engine_name','');

-- INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'openai','gpt','enable',0);
-- INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'openai','gpt','api_key','');

INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'aliyun','dashscope','enable',0);
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'aliyun','dashscope','api_key','');
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'aliyun','dashscope','engine_name','qwen-turbo');
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'aliyun','dashscope','engine_name','qwen-plus');


INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'baidu','qianfan','enable',0);
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'baidu','qianfan','api_key','');
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'baidu','qianfan','api_secre','');
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'baidu','qianfan','engine_name','ERNIE-Bot');
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'baidu','qianfan','engine_name','ERNIE-Bot-turbo');

INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'zhipu','zhipuai','enable',0);
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'zhipu','zhipuai','api_key','');
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'zhipu','zhipuai','engine_name','chatglm_turbo');


INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'lixiang','gpt','enable',0);
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'lixiang','gpt','api_key','');
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'lixiang','gpt','api_type','azure');
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'lixiang','gpt','api_base','');
INSERT INTO llm_config (`user_id`,`platform`,`model`,`key`,`value`) VALUES (1,'lixiang','gpt','api_version','');