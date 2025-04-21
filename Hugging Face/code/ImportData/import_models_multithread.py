import os
import json
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from neo4j import GraphDatabase
import pprint

# python3 -u "/home/yyz/cleaned_data/import_models_multithread.py"
# === 配置 Neo4j 连接 ===
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "xxxx"  # ⚠️ 替换为你的密码

# === 文件夹路径 ===
DATA_DIR = "./model_data"

# === 每个子进程创建独立 Neo4j driver ===
def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# === 加载所有模型数据，并附加来源文件名 ===
def load_all_models():
    model_entries = []
    for filename in os.listdir(DATA_DIR):
        if filename.startswith("data_") and filename.endswith(".json"):
            with open(os.path.join(DATA_DIR, filename), "r") as f:
                try:
                    data = json.load(f)
                    for item in data:
                        item["_source_file"] = filename
                        model_entries.append(item)
                except Exception as e:
                    print(f"❌ Failed to parse {filename}: {e}")
    return model_entries

# === 第一遍：写入模型节点、基本属性、非 base 关系 ===
def insert_model_pass1(entry):
    try:
        driver = get_driver()
        with driver.session() as session:
            session.run(
                "MERGE (m:Model {id: $id}) "
                "SET m.name = $name, m.downloads = $downloads, m.likes = $likes",
                id=entry["id"],
                name=entry["name"],
                downloads=entry.get("downloads", 0),
                likes=entry.get("likes", 0)
            )

            for lic in entry.get("licenses", []):
                if not isinstance(lic, str):
                    lic = str(lic)
                session.run("MERGE (l:License {name: $name})", name=lic)
                session.run(
                    "MATCH (m:Model {id: $id}), (l:License {name: $name}) "
                    "MERGE (m)-[:HAS_LICENSE]->(l)",
                    id=entry["id"], name=lic
                )

            for ds in entry.get("datasets", []):
                ds_id = ds.get("id") or "N/A"
                if not isinstance(ds_id, str): ds_id = str(ds_id)
                session.run(
                    "MATCH (d:Dataset {id: $dsid}) "
                    "MATCH (m:Model {id: $mid}) "
                    "MERGE (m)-[:USES_DATASET]->(d)",
                    mid=entry["id"], dsid=ds_id
                )

            for arch in entry.get("architectures", []):
                if not isinstance(arch, str): arch = str(arch)
                session.run("MERGE (a:Architecture {name: $name})", name=arch)
                session.run(
                    "MATCH (m:Model {id: $id}), (a:Architecture {name: $name}) "
                    "MERGE (m)-[:HAS_ARCHITECTURE]->(a)",
                    id=entry["id"], name=arch
                )
        driver.close()
    except Exception as e:
        print(f"❌ Pass1 Error: {entry.get('name')} ({entry.get('_source_file')}): {e}")
        pprint.pprint(entry)

# === 第二遍：写入 DERIVED_FROM 基座关系 ===
def insert_model_pass2(entry):
    try:
        driver = get_driver()
        with driver.session() as session:
            for base in entry.get("bases", []):
                if not isinstance(base, str): base = str(base)
                session.run("MERGE (b:Model {name: $name})", name=base)
                session.run(
                    "MATCH (m:Model {id: $id}), (b:Model {name: $name}) "
                    "MERGE (m)-[:DERIVED_FROM]->(b)",
                    id=entry["id"], name=base
                )
        driver.close()
    except Exception as e:
        print(f"❌ Pass2 Error: {entry.get('name')} ({entry.get('_source_file')}): {e}")
        pprint.pprint(entry)

# === 多进程运行辅助 ===
def run_parallel(data, func, desc):
    with Pool(processes=cpu_count()) as pool:
        list(tqdm(pool.imap_unordered(func, data), total=len(data), desc=desc))

# === 主函数 ===
def main():
    all_models = load_all_models()
    print(f"📦 共加载模型数：{len(all_models)}")

    print("🚀 第一遍：导入模型节点与基础属性")
    run_parallel(all_models, insert_model_pass1, "第一遍")

    print("🔁 第二遍：建立 DERIVED_FROM 关系")
    run_parallel(all_models, insert_model_pass2, "第二遍")

    print("✅ 所有模型导入完成（多进程双阶段）")

if __name__ == "__main__":
    main()
