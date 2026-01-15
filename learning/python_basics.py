# Lesson 1: Variables and Types
name = "Cloud Security"
risk_score = 0.85
is_risky = True

print(f"Project: {name}")
print(f"Risk: {risk_score}")
print(f"Is Risky: {is_risky}")

# Lesson 2: Lists
problems = ["public access", "no encryption", "no logs"]
print(f"Found {len(problems)} problems:")
for problem in problems:
    print(f"  - {problem}")

# Lesson 3: Dictionaries
config = {
    "bucket_name": "customer-data",
    "public": True,
    "encrypted": False
}
print(f"Bucket: {config['bucket_name']}")
print(f"Public: {config['public']}")

# Lesson 4: Functions
def calculate_risk(public, encrypted):
    risk = 0.0
    if public:
        risk += 0.5
    if not encrypted:
        risk += 0.3
    return risk

score = calculate_risk(public=True, encrypted=False)
print(f"Calculated risk: {score}")

# Lesson 5: If statements
if score > 0.7:
    decision = "BLOCK"
elif score > 0.3:
    decision = "WARN"
else:
    decision = "ALLOW"

print(f"Decision: {decision}")