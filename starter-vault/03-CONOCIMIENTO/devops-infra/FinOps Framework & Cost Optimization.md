---
tags: [cloud, finops, governance, cost-management]
categoria: devops-infra
---
# FinOps Framework & Cost Optimization

## ¿Qué es FinOps?
Disciplina operativa que combina finanzas, producto e ingeniería para maximizar el valor de negocio de cada dólar invertido en la nube (*Cloud Financial Management*).

## Fases del Ciclo FinOps
1. **Informar (Inform)**: Visibilidad de costos en tiempo real con etiquetado estricto (*Cost Allocation Tags*) en [[Terraform]].
2. **Optimizar (Optimize)**: Compra de Savings Plans / Reserved Instances, migración a Spot con [[Karpenter Kubernetes Node Autoscaler]] y ajuste de tamaño (*Right-Sizing*).
3. **Operar (Operate)**: Integración de métricas de costo unitario por usuario o transacción en dashboards de Grafana.
