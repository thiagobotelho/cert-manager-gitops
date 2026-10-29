#!/usr/bin/env python3
"""Verifica somente certificados públicos e cadeia/SPIFFE, sem exibir chaves."""
import base64
import json
import subprocess
from cryptography import x509
from cryptography.hazmat.primitives import hashes

def oc(*args):return subprocess.check_output(['oc','--request-timeout=30s']+list(args),text=True)
root=x509.load_pem_x509_certificate(oc('-n','istio-csr-vault','get','configmap/vault-mesh-root','-o','jsonpath={.data.root-cert\\.pem}').encode())
for deployment,account in [('httpbin','httpbin'),('sleep','sleep')]:
    dump=json.loads(oc('-n','mesh-vault-lab','exec','deployment/'+deployment,'-c','istio-proxy','--','pilot-agent','request','GET','config_dump'))
    verified=False
    for cfg in dump['configs']:
        for entry in cfg.get('dynamic_active_secrets',[]):
            chain=entry.get('secret',{}).get('tls_certificate',{}).get('certificate_chain',{})
            if not chain:continue
            pem=base64.b64decode(chain['inline_bytes']) if 'inline_bytes' in chain else chain['inline_string'].encode()
            certs=x509.load_pem_x509_certificates(pem)
            for child,parent in zip(certs,certs[1:]):child.verify_directly_issued_by(parent)
            if certs[-1].fingerprint(hashes.SHA256())!=root.fingerprint(hashes.SHA256()):certs[-1].verify_directly_issued_by(root)
            cert=certs[0]
            sans=cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value.get_values_for_type(x509.UniformResourceIdentifier)
            assert 'spiffe://cluster.local/ns/mesh-vault-lab/sa/'+account in sans
            assert (cert.not_valid_after_utc-cert.not_valid_before_utc).total_seconds() <= 3700
            print('PASS:',deployment,'cadeia Vault, SAN SPIFFE e validade curta; issuer='+cert.issuer.rfc4514_string())
            verified=True
    assert verified, 'certificado público do proxy não encontrado'
