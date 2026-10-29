# Cert-manager GitOps

Instala o **cert-manager Operator for Red Hat OpenShift** e entrega uma integração opcional com Vault PKI e istio-csr. O Operator instala/gerencia controller, cainjector e webhook; não é uma CA por si só.

| Componente | Função |
|---|---|
| Operator | Gerenciar ciclo de vida dos componentes cert-manager e do agente IstioCSR |
| Controller cert-manager | Reconciliar Certificate/CertificateRequest e solicitar assinatura ao Issuer |
| Webhook | Validar/defaultar recursos da API cert-manager |
| Cainjector | Manter bundles de CA nos recursos de integração selecionados |
| Issuer vault-pki | Autenticar no Vault e apontar ao endpoint PKI permitido |
| IstioCSR | Implantar o agente que autentica pedidos dos componentes Istio |

## Instalar

```bash
oc whoami
oc apply -k overlays/desenvolvimento
oc -n cert-manager-operator get subscription,csv,pods
oc -n cert-manager get pods
```

O canal stable-v1.20 recebe atualizações dessa linha com aprovação automática; startingCSV define o ponto inicial, sem bloquear futuras atualizações do canal. Antes de trocar canal, consulte compatibilidade da versão do OpenShift e de IstioCSR.

A instalação do Operator é independente da configuração Vault. Prossiga com [integração e arquitetura](docs/INTEGRACAO-MESH.md) depois do bootstrap de [vault-gitops](https://github.com/thiagobotelho/vault-gitops). Para emitir certificados de servidor e observar renovação, consulte [certificados e operação](docs/CERTIFICADOS.md).

Não há uma console web própria do cert-manager. Use Installed Operators/recursos do OpenShift, oc e condições dos objetos. A console do Vault administra a autoridade certificadora; Kiali mostra o mesh.

## Entradas

- operator/ e overlays/desenvolvimento/: somente instalação do Operator.
- integration/vault/: Issuer namespaced, TokenRequest RBAC e IstioCSR; exige PKI e confiança pública previamente configuradas.
- examples/certificate.yaml: exercício manual, fora das Applications.
- scripts/verify-certificates.py: valida certificados públicos dos proxies, cadeia Vault e SAN SPIFFE.

As Applications opcionais estão em argocd-gitops. Manifests não contêm token estático de Vault/Kubernetes nem chave de CA. Resultados de execução pertencem ao registro privado do operador.
