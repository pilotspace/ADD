"""engine_pin — single-source ENGINE_MD5 pin.

One constant, one home. The five prose-only suites import this value instead
of each carrying a duplicate hard-coded literal. When the engine legitimately
changes, re-aim this one line and the entire tooling suite re-anchors.

The pin is a hard-coded literal — never computed at runtime. A pin that
recomputes its own value from the file it is supposed to guard is vacuous:
it can never detect drift. The literal was recorded at the commit that first
introduced it and is updated only by a deliberate, human-approved task.
"""

ENGINE_MD5 = "a8ab76ae6ec1b7f525d2df1967242ee6"  # re-aimed @ status-pagination (cmd_status's milestones:/tasks[] lists now sort by `updated` desc + cap to 10 by default; new --all flag + JSON milestones_total/tasks_total fields). prior: ff7d9971… @ status-task-filter
ENGINE_PKG_MD5 = "de43f6f87be140724558e8b596f27c0f"  # re-aimed @ search-index (new add_engine/search.py module joins the add_engine/ package manifest digest — predicates.py/taskdoc.py/milestones.py/io_state.py untouched). prior: d79ea568… @ rule-id-coverage
