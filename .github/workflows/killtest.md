---
on: workflow_dispatch
permissions:
  contents: read
engine:
  id: claude
  command: ./stub_engine.py
steps:
  - name: Plant canaries A and C (strict-mode compliant)
    uses: ./.github/actions/export-canary
    with:
      value: ${{ secrets.SPIKE_CANARY }}
safe-outputs:
  threat-detection: false
  create-pull-request:
    draft: true
---

# Kill-test (SPIKE-01)

Stub engine, no model. Edit a file and open a pull request.
