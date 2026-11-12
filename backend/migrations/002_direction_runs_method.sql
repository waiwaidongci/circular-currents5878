-- Schema v2: direction_runs.method
-- 逐条研究(record，旧数据默认)与按日配对研究(daily，UTC日期对齐)的方法标记。
ALTER TABLE direction_runs ADD COLUMN method VARCHAR(20) NOT NULL DEFAULT 'record';
