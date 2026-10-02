# Source: NIST AI RMF measurement and monitoring guidance

Official primary-source webpages checked **2026-10-01**:

- [AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/), particularly Map 3.5, Measure 1.1/1.3/3.3 and Manage 2.1/4.1.
- [AI RMF Playbook: Measure](https://airc.nist.gov/airmf-resources/playbook/measure/), sections 2.4, 2.5 and 4.2.

Access scope: relevant webpage sections, not a full ingest of the framework PDF or complete Playbook. The pages identify the framework as AI RMF 1.0 (2023), with revision in progress. This voluntary guidance is not a Cashy-specific specification or empirical effectiveness study.

The Core calls for defined oversight processes, documenting risks that cannot be measured, independent assessment, appeals/feedback and monitoring. Manage 2.1 explicitly includes consideration of non-AI alternatives.

The Playbook discusses anomaly monitoring and later checks against reference information, validating whether proxy indicators measure their intended construct, documenting limits and subsequent human review. It also recommends interpreting operator/user feedback and override frequencies with relevant expertise.

Project inference, not a NIST scoring prescription: a transparent review-priority flag can be proposed without adding a predictive model, but cannot be labeled a calibrated probability of decision error without validation. See [[topics/cashy-manager-monitoring|manager monitoring]].
