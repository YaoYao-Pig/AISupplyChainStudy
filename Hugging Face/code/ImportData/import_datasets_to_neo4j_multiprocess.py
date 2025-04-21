from neo4j import GraphDatabase
import json
import csv
from multiprocessing import Pool, cpu_count
from functools import partial
from tqdm import tqdm
# python3 -u "/home/yyz/cleaned_data/import_to_neo4j_multiprocess.py"
# === 配置 Neo4j 连接信息 ===
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "xxx" 

# === 加载数据 ===
with open("./datasets.json", "r") as f:
    datasets = json.load(f)

with open("./chains.json", "r") as f:
    chains = json.load(f)

with open("license_changes.json", "r") as f:
    license_changes = json.load(f)

license_types = {}
with open("license_type_mapping.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 2:
            license_types[row[0]] = row[1]

# === 连接函数（每个进程独立连接） ===
def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# === 初始化 License 类型（只需一次） ===
def import_license_types():
    driver = get_driver()
    with driver.session() as session:
        for lic, typ in tqdm(license_types.items(), desc="导入 License 类型"):
            session.run("MERGE (l:License {name: $name}) SET l.type = $type", name=lic, type=typ)
    driver.close()

# === 子进程：导入单个 Dataset ===
def import_single_dataset(ds):
    driver = get_driver()
    with driver.session() as session:
        doi_value = ds["doi"] if ds["doi"] is not None else "N/A"
        session.run(
            "MERGE (d:Dataset {id: $id}) "
            "SET d.internal_id = $internal_id, d.likes = $likes, d.downloads = $downloads, d.doi = $doi",
            id=ds["id"],
            internal_id=ds["internal_id"],
            likes=ds["likes"],
            downloads=ds["downloads"],
            doi=doi_value
        )
        for lic in ds.get("license", []):
            session.run("MERGE (l:License {name: $name})", name=lic)
            session.run(
                "MATCH (d:Dataset {id: $id}), (l:License {name: $lic}) "
                "MERGE (d)-[:HAS_LICENSE]->(l)",
                id=ds["id"], lic=lic
            )
        for task in ds.get("tasks", []):
            session.run("MERGE (t:Task {name: $name})", name=task)
            session.run(
                "MATCH (d:Dataset {id: $id}), (t:Task {name: $task}) "
                "MERGE (d)-[:HAS_TASK]->(t)",
                id=ds["id"], task=task
            )
    driver.close()

# === 子进程：导入 License 变更 ===
def import_single_license_change(change):
    driver = get_driver()
    with driver.session() as session:
        session.run("MERGE (a:License {name: $start})", start=change["start"])
        session.run("MERGE (b:License {name: $end})", end=change["end"])
        session.run(
            "MATCH (a:License {name: $start}), (b:License {name: $end}) "
            "MERGE (a)-[r:CHANGED_TO]->(b) SET r.count = $count",
            start=change["start"], end=change["end"], count=change["count"]
        )
    driver.close()

# === 子进程：导入模型链条 ===
def import_single_chain(chain_item):
    chain_name, paths = chain_item
    driver = get_driver()
    with driver.session() as session:
        session.run("MERGE (c:Chain {name: $name})", name=chain_name)
        for path in paths:
            for i in range(len(path) - 1):
                src = path[i]
                tgt = path[i + 1]
                for m in [src, tgt]:
                    session.run("MERGE (m:Model {name: $name})", name=m["model"])
                    for lic in m.get("license", []):
                        session.run("MERGE (l:License {name: $name})", name=lic)
                        session.run(
                            "MATCH (m:Model {name: $model}), (l:License {name: $lic}) "
                            "MERGE (m)-[:HAS_LICENSE]->(l)",
                            model=m["model"], lic=lic
                        )
                session.run(
                    "MATCH (a:Model {name: $src}), (b:Model {name: $tgt}) "
                    "MERGE (a)-[:DERIVED_TO]->(b)",
                    src=src["model"], tgt=tgt["model"]
                )
            session.run(
                "MATCH (c:Chain {name: $chain}), (m:Model {name: $start}) "
                "MERGE (c)-[:STARTS_FROM]->(m)",
                chain=chain_name, start=path[0]["model"]
            )
    driver.close()

# === 并行处理函数 ===
def run_parallel(data, func, desc):
    with Pool(processes=cpu_count()) as pool:
        list(tqdm(pool.imap_unordered(func, data), total=len(data), desc=desc))

# === 主流程 ===
if __name__ == "__main__":
    import_license_types()
    run_parallel(datasets, import_single_dataset, "导入 Datasets")
    run_parallel(license_changes, import_single_license_change, "导入 License 变更")
    run_parallel(list(chains.items()), import_single_chain, "导入 Chains")
    print("多进程导入完成")
