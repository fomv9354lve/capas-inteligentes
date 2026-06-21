import sys; sys.path.insert(0,".")
import capas_ezkl, capas_verify, json
# PROVER side: prove CHG = AVAL - BASE  (weights [1,-1]) on inputs [10,8] -> 2
arts = capas_ezkl.prove_linear_derivation([1.0,-1.0],[10.0,8.0],"/tmp/ezkl_demo")
print("ezkl artifacts:", {k:v.split('/')[-1] for k,v in arts.items()})
# CAPAS verifies the REAL succinct proof through the proof-carrying gate
payload={"claim":{"id":"ezkl_chg","text":"Derived CHG via verified circuit","type":"financial_metric_claim"},
 "evidence":{"reported_value":1.0,"reference_value":1.0,"tolerance":1.0,"metric_period_match":True,
   "zk_proof":{"scheme":"ezkl-kzg","verifying_key_id":"ezkl","statement":{"circuit":"CHG=AVAL-BASE"},
               "public_inputs":{}, "proof":arts}},
 "schema_version":"capas-claim-payload-v3"}
r=capas_verify.verify(payload)
print("verdict:", r["verified_verdict"], "| scope:", r["scope"], "| tier:", r["verification_tier"])
for c in r["checks"]:
    if c["check"]=="zk_proof": print("zk check:", c["status"], c["detail"].get("scheme"))
