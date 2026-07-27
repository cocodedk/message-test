---
title: Fixture document
---

# Quarterly platform review

The platform team spent the quarter reducing the time it takes a new service to
reach production. At the start of the quarter that journey took eleven working
days, most of which was waiting rather than working. Two thirds of the elapsed
time sat in queues: waiting for a security review slot, waiting for a namespace
to be provisioned, and waiting for someone to approve a change that nobody had
raised an objection to. The work itself was rarely the bottleneck.

We attacked the queues rather than the work. Security review moved from a
scheduled meeting to an automated policy check with a human escalation path for
the cases the checker could not decide. Namespace provisioning became a
self-service template that a team applies without asking anyone. Change approval
now happens by default after a fixed interval unless a reviewer actively objects,
which inverts the burden of proof and removes the most common source of delay.

The result is a median of three working days from first commit to production
traffic, measured across forty-one services. The remaining delay is concentrated
in two places. Services that touch payment data still require a manual review,
which we think is correct and do not plan to change. Services with database
migrations wait for a maintenance window, which we think is not correct and plan
to address next quarter by supporting online schema changes.

```python
# Code fences should be stripped before the passage is selected.
def excluded():
    return "this text must not appear in the cloze passage"
```

Two risks are worth recording. The automated policy checker now sits on the
critical path for every deployment, so its own availability matters more than it
did when review was a meeting. And the default-approve rule depends on reviewers
reading notifications promptly, which is a behaviour rather than a mechanism, and
behaviours decay when people are busy.
