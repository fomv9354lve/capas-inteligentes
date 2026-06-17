# Quimb Fidelity Estimate Audit

Question:

> Is `quimb.tensor.CircuitMPS.fidelity_estimate()` a formal truncation bound or
> an empirical/algorithmic estimate?

## Source Read

In the installed environment:

- `quimb==1.14.0`
- file: `.pixi/envs/default/lib/python3.12/site-packages/quimb/tensor/circuit.py`

`CircuitMPS.fidelity_estimate()` source:

```python
def fidelity_estimate(self):
    r"""Estimate the fidelity of the current state based on its norm, which
    tracks how much the state has been truncated:

    .. math::

        \tilde{F} =
        \left| \langle \psi | \psi \rangle \right|^2
        \approx
        \left|\langle \psi_\mathrm{ideal} | \psi \rangle\right|^2
    """
    cur_orthog = self.gate_opts["info"].get("cur_orthog", None)

    if cur_orthog is None:
        return abs(self._psi.norm()) ** 2

    cmin, cmax = cur_orthog
    return abs(self._psi[cmin : cmax + 1].norm(tags=all)) ** 2
```

`CircuitMPS.error_estimate()` source:

```python
def error_estimate(self):
    r"""Estimate the error in the current state based on the norm of the
    discarded part of the state:

    .. math::

        \epsilon = 1 - \tilde{F}
    """
    return 1 - self.fidelity_estimate()
```

## Conclusion

The API itself calls the quantity an estimate and uses an approximate relation
between truncated-state norm and ideal-state overlap.

Therefore CAPAS must not label this as a formal certificate.

Correct CAPAS label:

```text
physical_evidence_level = estimated_bound
certification_status = estimated_not_formal_certificate
verification_independence = algorithmic_error_certificate_same_runtime
```

Incorrect label:

```text
physical_evidence_level = certified_bound
```

## Open Path To Formal Bound

A future `formal_bound` level requires a quantity that is mathematically tied to
the discarded Schmidt weight/truncation norm and whose assumptions are explicit.
It should not be added until a trace carries an actual formal bound and the
bound is documented independently of quimb's fidelity estimate wording.
