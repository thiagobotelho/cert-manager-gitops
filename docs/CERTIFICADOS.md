# Certificados e diagnóstico

## Definir o certificado desejado

Em examples/certificate.yaml, dnsNames define os nomes aceitos pelo servidor, duration a validade, renewBefore a antecedência da renovação e secretName o destino. issuerRef seleciona a CA por meio do Issuer. privateKey.rotationPolicy=Always solicita chave nova quando o certificado é reemitido.

```bash
oc apply -f examples/certificate.yaml
oc -n istio-vault-system get certificate,certificaterequest
oc -n istio-vault-system describe certificate vault-demo
```

Observe Ready, notAfter, renewalTime e revision. O controller agenda renovação antes do vencimento. Uma mudança relevante da especificação pode iniciar reemissão. Para renovação manual, use cmctl renew com a versão compatível do cliente; não apague o Secret para forçar renovação.

A renovação atualiza o Secret. Cada servidor precisa recarregar seu certificado. No mesh, o agente e SDS cuidam do certificado de workload; não existe um rollout manual obrigatório para cada renovação de identidade.

## Diagnóstico por objeto

| Objeto / etapa | Conferir |
|---|---|
| Subscription / CSV | Canal disponível, InstallPlan e pods do Operator |
| Issuer | Ready e autenticação/CA HTTPS do Vault |
| Certificate | Especificação, validade, Secret de destino e condições |
| CertificateRequest | Aprovação, erro de assinatura e policy do Vault |
| IstioCSR | Ready, endpoint gRPC, IssuerRef e raiz pública |
| Proxy | Certificado carregado, cadeia, SAN e conexão com CA |

Não publique Secrets inteiros, dumps de chave ou JWTs. Para inspecionar o certificado público, use jsonpath somente para tls.crt e openssl x509, conforme o guia PKI do Vault.

## Testes negativos úteis

- Conta/namespace/audience não vinculados à role Vault devem falhar no login.
- DNS fora dos allowed_domains e URI fora dos allowed_uri_sans devem ser recusados.
- Validade acima do max_ttl deve ser recusada ou limitada conforme a operação; confira a validade efetiva.
- Cliente sem proxy/certificado deve falhar contra PeerAuthentication STRICT.
- Identidade válida com operação não permitida deve receber recusa de AuthorizationPolicy.

Execute em recursos descartáveis e remova apenas os objetos criados para o exercício. Uma falha DNS ou falta de rota não demonstra negação de identidade. Não reutilize certificados/chaves de outro ambiente para simplificar os exemplos.
