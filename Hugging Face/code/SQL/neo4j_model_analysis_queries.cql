// === 节点总数 ===
MATCH (n)
RETURN count(n) AS total_nodes;

// === 不同类型节点的数量 ===
MATCH (n)
RETURN labels(n)[0] AS node_type, count(*) AS count
ORDER BY count DESC;

// === 每种关系的数量 ===
MATCH ()-[r]->()
RETURN type(r) AS relationship_type, count(*) AS count
ORDER BY count DESC;

// === 模型按架构统计 ===
MATCH (m:Model)-[:HAS_ARCHITECTURE]->(a:Architecture)
RETURN a.name AS architecture, count(m) AS model_count
ORDER BY model_count DESC;

// === 使用最频繁的数据集（热点）===
MATCH (m:Model)-[:USES_DATASET]->(d:Dataset)
RETURN d.name AS dataset, count(m) AS model_count
ORDER BY model_count DESC
LIMIT 20;

// === 被最多模型衍生的 base 模型 ===
MATCH (m:Model)<-[:DERIVED_FROM]-(derived:Model)
RETURN m.name AS base_model, count(derived) AS derived_count
ORDER BY derived_count DESC
LIMIT 10;

// === 模型点赞数分布 ===
MATCH (m:Model)
WITH m.likes AS likes
RETURN
  CASE
    WHEN likes < 10 THEN "<10"
    WHEN likes < 50 THEN "10-49"
    WHEN likes < 100 THEN "50-99"
    ELSE "100+"
  END AS like_range,
  count(*) AS model_count
ORDER BY like_range;

// === 每个模型的连接关系数量（度数）===
MATCH (m:Model)
RETURN m.name AS model, size((m)--()) AS connection_count
ORDER BY connection_count DESC
LIMIT 20;

// === 查询两个模型之间的最短路径（可替换名称）===
MATCH (a:Model {name: "modelA"}), (b:Model {name: "modelB"}),
path = shortestPath((a)-[*..10]-(b))
RETURN path;

// === 查看所有模型之间的 DERIVED_FROM 层级结构 ===
MATCH path = (m:Model)-[:DERIVED_FROM*]->(base:Model)
RETURN path
LIMIT 100;
