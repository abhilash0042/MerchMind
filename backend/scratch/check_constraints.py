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
cur.execute("""
SELECT conname, contype, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'orders'::regclass;
""")
rows = cur.fetchall()
print("Constraints on Orders:")
for r in rows:
    print(r)

cur.close()
conn.close()
