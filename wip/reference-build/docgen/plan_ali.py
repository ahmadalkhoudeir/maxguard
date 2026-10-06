"""Ali's tasks: model shortlist and licenses, evaluation set, benchmark, model choice."""

from plan_helpers import checklist, pr_step, start_step

TASKS = [
    {
        "id": "ALI-01", "owner": "ali", "milestone": "W1",
        "title": "Model shortlist and license check",
        "labels": ["area:ai"], "status": "process",
        "depends": [],
        "goal": (
            "Start `docs/model-eval/README.md`: the two hardware tiers, the shortlist of models "
            "for each, and for every model its license, whether MaxGuard may ship it in the "
            "offline bundle, and exactly what notice or attribution that requires. License is a "
            "hard gate: a model we may not redistribute cannot be the default."
        ),
        "prereq": "None. You can start in Week 1.",
        "steps": [
            start_step("ali/model-shortlist"),
            "Create `docs/model-eval/README.md` with this starting text. It was drafted in "
            "planning from search results, because the model sites (Hugging Face, ollama.com, "
            "Google, Meta) were blocked there:\n\n@@FILE docs/model-eval/README.md@@",
            "**Check every row of section 2 against the primary source** and fix the file: open "
            "each model's own license (the Hugging Face model card's LICENSE file, Meta's Llama "
            "license page, Google's Gemma Terms of Use, IBM's Granite repository), and for "
            "Ollama also run `ollama show --license <tag>` after pulling. Watch for one trap: a "
            "GitHub repository's license can cover only the *code* in it, not the model weights "
            "(Google's `gemma` library is Apache-2.0, but the Gemma *models* are under the Gemma "
            "Terms of Use).",
            "Add a column **Checked on** with the date and the exact URL you read, and remove "
            "every \"read the license file before shipping\" warning you resolved.",
            "Post the shortlist in Discussions (category *Ideas*) and ask Jonattan and Ahmad "
            "whether any model should be added or removed before ALI-04 runs.",
            pr_step("docs: model shortlist with verified licenses (ALI-01)", "MeliorExi"),
        ],
        "files": [("docs/model-eval/README.md", "snip:model_eval_README.md")],
        "commands": [],
        "test": "Every row in section 2 names a license you read yourself, with a link and a "
                "date, and the redistribution duties match that license's text.",
        "why": (
            "The offline bundle copies the model onto the user's computer, which is "
            "redistribution, so the license applies to the team, not only to the user. Custom "
            "licenses (Llama, Gemma) add duties such as a notice file, an attribution line, or "
            "passing on a use policy; missing one is a license violation in a public project. "
            "Checking the primary source matters because search results and summaries mix up "
            "code licenses and model licenses."
        ),
        "checklist": checklist(extra=["Every license row has a primary-source link and a date"]),
    },
    {
        "id": "ALI-02", "owner": "ali", "milestone": "W2",
        "title": "Evaluation set: the same 13 questions for every model",
        "labels": ["area:ai"],
        "depends": ["FIO-02", "JAK-03", "AMO-01", "JAI-03"],
        "goal": (
            "Write `scripts/make_eval_set.py`, which turns the fixture logs into the evaluation "
            "set: one item per rule, holding the finding exactly as the pipeline gives it to the "
            "AI plus the raw log records it cites. Every model is then asked the same questions."
        ),
        "prereq": "FIO-02 and JAK-03 (rules), AMO-01 (mapping files) and JAI-03 (record lookup) "
                  "are merged.",
        "steps": [
            start_step("ali/eval-set"),
            "Create `scripts/make_eval_set.py`:\n\n@@FILE scripts/make_eval_set.py@@",
            "Build the set and commit the result `tests/fixtures/ai_eval/eval_set.json`:\n\n@@RUN build@@",
            "Run it a second time and check that nothing changed (the file must be identical "
            "byte for byte):\n\n@@RUN again@@",
            pr_step("feat: AI evaluation set built from the fixtures (ALI-02)", "MeliorExi"),
        ],
        "files": ["scripts/make_eval_set.py"],
        "commands": [
            {"id": "build", "show": "python -m scripts.make_eval_set"},
            {"id": "again", "show": ("cp tests/fixtures/ai_eval/eval_set.json /tmp/eval_set_1.json\n"
                                     "python -m scripts.make_eval_set\n"
                                     "cmp tests/fixtures/ai_eval/eval_set.json /tmp/eval_set_1.json && echo identical")},
        ],
        "test": "The script reports 13 items for 13 rules, and the second run prints `identical`.",
        "why": (
            "Comparing models only works if every model answers exactly the same questions with "
            "exactly the same evidence. Building the set from the same fixtures and the same code "
            "path as the real pipeline means the evaluation measures what users will see, and a "
            "deterministic file shows up in a pull request diff whenever a rule or mapping changes."
        ),
        "checklist": checklist(extra=["`tests/fixtures/ai_eval/eval_set.json` is committed"]),
    },
    {
        "id": "ALI-03", "owner": "ali", "milestone": "W3",
        "title": "Benchmark script: speed, citations, and unsupported details",
        "labels": ["area:ai"],
        "depends": ["ALI-02", "JON-02"],
        "goal": (
            "Write `scripts/benchmark_models.py`: for each model, run the evaluation set through "
            "MaxGuard's own `explain()` twice and record per question the seconds taken, sentences "
            "kept and dropped by the citation check, \"unsupported details\" (an address, port, "
            "host name, TLS version or cipher that is not in the evidence), and whether run 2 gave "
            "the same answer as run 1."
        ),
        "prereq": "ALI-02 and JON-02 (the Ollama client) are merged.",
        "steps": [
            start_step("ali/benchmark"),
            "Create `scripts/benchmark_models.py`:\n\n@@FILE scripts/benchmark_models.py@@",
            "Create the tests `tests/unit/test_benchmark.py`. They replace the model with a fake "
            "`explain()`, so no Ollama is needed:\n\n@@FILE tests/unit/test_benchmark.py@@",
            "Run them:\n\n@@RUN tests@@",
            "Check the error path without Ollama running (the address points at a closed port):\n\n"
            "@@RUN noollama@@",
            pr_step("feat: model benchmark on the evaluation set (ALI-03)", "MeliorExi"),
        ],
        "files": ["scripts/benchmark_models.py", "tests/unit/test_benchmark.py",
                  "tests/fixtures/ai_eval/eval_set.json"],
        "commands": [
            {"id": "tests", "show": "pytest tests/unit/test_benchmark.py -q"},
            {"id": "noollama", "show": ("OLLAMA_HOST=http://127.0.0.1:1 python -m scripts.benchmark_models "
                                        "--tier laptop qwen3:4b"), "expect_code": 1},
        ],
        "test": "`pytest` passes, and without Ollama the script stops with a clear message and "
                "exit code 1 instead of a traceback.",
        "why": (
            "Speed alone picks the wrong model: a fast model that invents details is worse than "
            "useless in a security tool. The citation check catches made-up record IDs, and the "
            "unsupported-detail check catches made-up facts *inside* a sentence that cites real "
            "records. Running twice checks that temperature 0 and a fixed seed really give "
            "repeatable answers on your hardware."
        ),
        "checklist": checklist(),
    },
    {
        "id": "ALI-04", "owner": "ali", "milestone": "W4",
        "title": "Run the benchmark on both tiers and propose the default models",
        "labels": ["area:ai", "critical-path"], "status": "process", "hardware": True,
        "depends": ["ALI-01", "ALI-03"],
        "goal": (
            "Run the benchmark on a Pi-class machine (models of 4B parameters or fewer) and on a "
            "laptop (8B or fewer), review the answers by hand, and propose one default model per "
            "tier. The choice replaces `TEMPORARY_DEFAULT_MODEL` in "
            "`maxguard/ai/ollama_client.py` and goes into the offline bundle (JON-05)."
        ),
        "prereq": "ALI-01 and ALI-03 are merged; Ollama 0.35.1 is installed on both machines.",
        "steps": [
            start_step("ali/model-results"),
            "Pull the shortlisted models on each machine (`ollama pull <tag>`), then follow "
            "sections 5.1 and 5.2 of `docs/model-eval/README.md` to run, for example:\n\n"
            "```bash\npython -m scripts.benchmark_models --tier pi qwen3:4b llama3.2:3b phi4-mini gemma3:4b\n```\n\n"
            "*Not run in planning (no model could be downloaded); verify on hardware.*",
            "Fill in section 6 (results per tier) from `docs/model-eval/raw_results.csv`, then the "
            "human review: read every kept sentence of the two best models and mark any that is "
            "wrong even though it cites real records.",
            "Write section 7: your proposal for each tier, with the reasons (grounding first, then "
            "license, then speed). Changing the default model updates "
            "`docs/PROJECT_DECISIONS.md`, so Ahmad (Security Lead) approves the pull request.",
            "In the same pull request, set `TEMPORARY_DEFAULT_MODEL` to the laptop-tier choice and "
            "rename it `DEFAULT_MODEL` (Jonattan reviews that change).",
            pr_step("docs: model evaluation results and default models (ALI-04)", "MeliorExi"),
        ],
        "files": [], "commands": [],
        "test": "Section 6 has real numbers for both tiers, every proposed model passed the "
                "license gate in section 2, and the unit tests still pass after the constant changes.",
        "why": (
            "The model is the one part of MaxGuard that can be confidently wrong. Measuring "
            "dropped sentences and unsupported details on the same questions, and then reading the "
            "answers yourself, is how the team picks a model it can defend in the final "
            "presentation."
        ),
        "checklist": checklist(extra=["Ahmad approved the choice",
                                      "`raw_results.csv` is committed"]),
    },
    {
        "id": "ALI-05", "owner": "ali", "milestone": "S8",
        "title": "Re-evaluate the models against prompt injection and the spring rules",
        "labels": ["area:ai"], "status": "process", "hardware": True,
        "depends": ["ALI-04", "JON-06"],
        "goal": (
            "Run the evaluation again on both tiers with Jonattan's prompt-injection set and the "
            "spring rules (JA4 watchlist, decoys, baselines), and confirm or change the default "
            "models before the v2.0 feature freeze."
        ),
        "prereq": "ALI-04 and JON-06 are merged; the spring rules you evaluate are merged.",
        "steps": [
            start_step("ali/eval-spring"),
            "Regenerate the evaluation set once the spring rules and their fixtures are merged "
            "(`python -m scripts.make_eval_set`), so it has one item per rule, and commit it "
            "(`tests/unit/test_benchmark.py` checks it is up to date).",
            "On each tier, run the benchmark on both sets, then count how often each model obeyed "
            "the hostile text:\n\n"
            "```bash\n"
            "python -m scripts.benchmark_models --tier pi qwen3:4b llama3.2:3b\n"
            "python -m scripts.benchmark_models --tier pi "
            "--eval-set tests/fixtures/ai_eval/injection/injection_set.json qwen3:4b llama3.2:3b\n"
            "python -m scripts.injection_report docs/model-eval/raw_results.csv\n"
            "```\n\n"
            "\"Obeyed\" means the canary word reached a sentence MaxGuard kept. The citation check "
            "cannot catch those sentences when they cite the hostile record itself (JON-06 explains "
            "why), so this rate is a real difference between models. *Not run in planning (no "
            "model could be downloaded); verify on hardware.*",
            "Add a section 10 to `docs/model-eval/README.md`: the new results per tier, the "
            "injection rate per model, and whether the default models stay. A change of default "
            "model needs Ahmad's approval, as in ALI-04.",
            pr_step("docs: spring model re-evaluation (ALI-05)", "MeliorExi"),
        ],
        "files": [], "commands": [],
        "test": "The new results cover every spring rule and the injection set on both tiers.",
        "why": (
            "New rules mean new kinds of evidence (fingerprints, decoy contacts, baselines) that "
            "the model has never been tested on, and newer model versions appear every few months. "
            "A model that often obeys text from the network is a bad default even if its other "
            "numbers are good. A second evaluation before the feature freeze keeps the choice honest."
        ),
        "checklist": checklist(extra=["Ahmad approved any change of default model"]),
    },
]
