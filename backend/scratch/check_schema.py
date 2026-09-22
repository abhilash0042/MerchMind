import psycopg2

conn = psycopg2.connect(
    host="aws-1-ap-south-1.pooler.supabase.com",
    port=5432,
    dbname="postgres",
    user="postgres.gwwhksdelequvapksgqx",
    password="Abhilash@142",
    sslmode="require"
)
cur = conn.cursor()
cur.execute("SELECT column_name, generation_expression FROM information_schema.columns WHERE table_name = 'orders' AND generation_expression IS NOT NULL;")
rows = cur.fetchall()
print("Generated Columns in Orders:")
for r in rows:
    print(r)

cur.execute("SELECT column_name, generation_expression FROM information_schema.columns WHERE table_name = 'pricing_snapshots' AND generation_expression IS NOT NULL;")
rows2 = cur.fetchall()
print("Generated Columns in Pricing:")
for r in rows2:
    print(r)
    
cur.close()
conn.close()
