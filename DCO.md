# Developer Certificate of Origin

CAPAS requires every commit to be signed off under the **Developer Certificate of Origin (DCO),
version 1.1**. Signing off is a per-commit attestation that you have the right to submit the work
under the project's open-source license — see [`CONTRIBUTING.md`](CONTRIBUTING.md#sign-your-commits-dco)
for how to do it (`git commit -s`).

The canonical text is published at <https://developercertificate.org> and reproduced verbatim below.

---

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

---

## How to sign off

Add the `-s` (`--signoff`) flag to your commit:

```bash
git commit -s -m "Your message"
```

Git appends a trailer using your configured `user.name` and `user.email`:

```
Signed-off-by: Jane Doe <jane@example.com>
```

That trailer is your DCO certification for that commit. Use a real name and a reachable email that
match the commit author.
