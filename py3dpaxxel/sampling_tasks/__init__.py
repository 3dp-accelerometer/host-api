"""
**Terminology**

- **Step**: one single pattern trajectory

  - i.e. back and forth movement
  - exact trajectory depends on pattern generator

- **Steps**: repetitions of **Step**

  - mostly referred as `step_repeat_count`
  - captured within a single stream (single output file)

- **Record**: a single recording session

  - may contain one single **Step** or many **Steps**
  - consists of one stream
  - stored in one single output file

- **Sequence**: repetitions of **Records**

  - mostly referred as `sequence_repeat_count`
  - captured within multiple `Steps` streams (multiple output files)

- **Stream**: list of samples received from controller

  - consists of

    - header (first package),
    - `0` to `N` samples (intermediate packages),
    - other status packages (optional)
    - and stop package (last package)

"""
