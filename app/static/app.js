// 渐进增强标记：没有 JS 时，步骤直接展示，提交表单不可用。
document.documentElement.classList.add("js");

function csrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : "";
}

// ---------- 步骤动画 ----------

document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) {
        return;
    }

    const button = event.target.closest("[data-action]");
    if (!button) {
        return;
    }

    const player = button.closest(".step-player");
    if (!player) {
        return;
    }

    const steps = Array.from(player.querySelectorAll(".step"));
    if (steps.length === 0) {
        return;
    }

    const indicator = player.querySelector(".step-indicator");
    let current = steps.findIndex((step) => step.classList.contains("is-active"));
    if (current < 0) {
        current = 0;
    }

    const action = button.dataset.action;
    if (action === "prev") {
        current = Math.max(0, current - 1);
    } else if (action === "next") {
        current = Math.min(steps.length - 1, current + 1);
    } else if (action === "replay") {
        current = 0;
    } else {
        return;
    }

    setStep(player, steps, current, indicator);
});

function setStep(player, steps, current, indicator) {
    steps.forEach((step, index) => {
        step.classList.toggle("is-active", index === current);
    });

    if (indicator) {
        indicator.textContent = `${current + 1} / ${steps.length}`;
    }

    const prevButton = player.querySelector('[data-action="prev"]');
    const nextButton = player.querySelector('[data-action="next"]');
    if (prevButton) {
        prevButton.disabled = current === 0;
    }
    if (nextButton) {
        nextButton.disabled = current === steps.length - 1;
    }
}

document.querySelectorAll(".step-player").forEach((player) => {
    const steps = Array.from(player.querySelectorAll(".step"));
    if (steps.length === 0) {
        return;
    }

    const indicator = player.querySelector(".step-indicator");
    let current = steps.findIndex((step) => step.classList.contains("is-active"));
    if (current < 0) {
        current = 0;
    }
    setStep(player, steps, current, indicator);
});

// ---------- 卡片放大查看 ----------

const lightbox = createLightbox();
let lightboxLastFocus = null;

document.querySelectorAll(".v-card, .v-compare, .v-callout").forEach((card) => {
    if (card.closest(".lightbox")) {
        return;
    }

    card.classList.add("is-zoomable");
    card.tabIndex = 0;
    card.setAttribute("role", "button");
    card.setAttribute("aria-haspopup", "dialog");

    const heading = card.querySelector("h4, strong");
    const label =
        heading && heading.textContent.trim()
            ? heading.textContent.trim()
            : "卡片";
    card.setAttribute("aria-label", `放大查看：${label}`);

    const hint = document.createElement("span");
    hint.className = "card-zoom-hint";
    hint.textContent = "点击放大";
    card.appendChild(hint);
});

document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) {
        return;
    }

    if (lightbox.contains(event.target)) {
        if (event.target === lightbox) {
            closeLightbox();
        }
        return;
    }

    if (event.target.closest("a, button, input, textarea, select, summary")) {
        return;
    }

    const card = event.target.closest(".is-zoomable");
    if (!card) {
        return;
    }

    openLightbox(card);
});

document.addEventListener("keydown", (event) => {
    if (lightbox.hidden) {
        return;
    }

    if (event.key === "Escape") {
        event.preventDefault();
        closeLightbox();
        return;
    }

    if (event.key === "Tab") {
        trapLightboxFocus(event);
    }
});

document.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") {
        return;
    }
    if (!(event.target instanceof Element)) {
        return;
    }
    if (event.target.closest("a, button, input, textarea, select, summary")) {
        return;
    }

    const card = event.target.closest(".is-zoomable");
    if (!card) {
        return;
    }

    event.preventDefault();
    openLightbox(card);
});

function createLightbox() {
    const box = document.createElement("div");
    box.className = "lightbox";
    box.hidden = true;
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.setAttribute("aria-label", "放大查看卡片");

    const panel = document.createElement("div");
    panel.className = "lightbox-panel";

    const close = document.createElement("button");
    close.className = "lightbox-close";
    close.type = "button";
    close.setAttribute("aria-label", "关闭放大查看");
    close.textContent = "×";
    close.addEventListener("click", closeLightbox);

    const content = document.createElement("div");
    content.className = "lightbox-content";

    panel.append(close, content);
    box.appendChild(panel);
    document.body.appendChild(box);
    return box;
}

function openLightbox(card) {
    const content = lightbox.querySelector(".lightbox-content");
    const close = lightbox.querySelector(".lightbox-close");
    if (!content || !close) {
        return;
    }

    const clone = card.cloneNode(true);
    clone.classList.remove("is-zoomable");
    clone.removeAttribute("tabindex");
    clone.removeAttribute("role");
    clone.removeAttribute("aria-haspopup");
    clone.removeAttribute("aria-label");
    clone.querySelectorAll(".card-zoom-hint").forEach((hint) => hint.remove());

    content.replaceChildren(clone);
    lightboxLastFocus = card;
    lightbox.hidden = false;
    document.body.classList.add("lightbox-open");
    requestAnimationFrame(() => lightbox.classList.add("is-open"));
    close.focus();
}

function closeLightbox() {
    if (lightbox.hidden) {
        return;
    }

    lightbox.classList.remove("is-open");
    lightbox.hidden = true;
    const content = lightbox.querySelector(".lightbox-content");
    if (content) {
        content.replaceChildren();
    }
    document.body.classList.remove("lightbox-open");

    if (lightboxLastFocus) {
        lightboxLastFocus.focus();
        lightboxLastFocus = null;
    }
}

function trapLightboxFocus(event) {
    const focusables = lightbox.querySelectorAll(
        'button, [href], summary, input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (focusables.length === 0) {
        return;
    }

    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
    }
}

// ---------- 项目任务标记完成 ----------

document.addEventListener("click", async (event) => {
    if (!(event.target instanceof Element)) {
        return;
    }

    const button = event.target.closest("[data-complete-lesson]");
    if (!button) {
        return;
    }

    await completeLesson(button);
});

async function completeLesson(button) {
    const lessonId = button.dataset.completeLesson;
    const panel = button.closest(".project-complete");
    const resultBox = panel ? panel.querySelector("[data-complete-result]") : null;
    const originalText = button.textContent.trim();

    button.disabled = true;
    button.textContent = "标记中…";
    if (resultBox) {
        resultBox.hidden = true;
    }

    try {
        const response = await fetch(
            `/api/lessons/${encodeURIComponent(lessonId)}/complete`,
            {
                method: "POST",
                credentials: "same-origin",
                headers: { "X-CSRF-Token": csrfToken() },
            }
        );

        if (response.status === 401) {
            window.location.assign("/login");
            return;
        }

        const data = await response.json().catch(() => null);
        if (!response.ok || !data) {
            showProjectResult(resultBox, extractErrorMessage(data));
            button.disabled = false;
            button.textContent = originalText;
            return;
        }

        showProjectResult(resultBox, data.message || "本课已完成");
        window.location.assign("/roadmap");
    } catch (error) {
        showProjectResult(resultBox, "网络异常，请确认服务是否在运行");
        button.disabled = false;
        button.textContent = originalText;
    }
}

function showProjectResult(box, message) {
    if (!box) {
        return;
    }
    box.hidden = false;
    box.textContent = message;
}

// ---------- 本地作业标记完成 ----------

document.addEventListener("click", async (event) => {
    if (!(event.target instanceof Element)) {
        return;
    }

    const button = event.target.closest("[data-complete-exercise]");
    if (!button) {
        return;
    }

    await completeLocalTask(button);
});

document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) {
        return;
    }

    const button = event.target.closest("[data-reset-local]");
    if (!button) {
        return;
    }

    const card = button.closest(".exercise-card");
    if (!card) {
        return;
    }

    setLocalTaskCompleted(card, false);
});

async function completeLocalTask(button) {
    const exerciseId = button.dataset.completeExercise;
    const card = button.closest(".exercise-card");
    if (!exerciseId || !card) {
        return;
    }

    const originalText = button.textContent.trim();
    button.disabled = true;
    button.textContent = "标记中…";

    try {
        const response = await fetch(
            `/api/exercises/${encodeURIComponent(exerciseId)}/complete`,
            {
                method: "POST",
                credentials: "same-origin",
                headers: { "X-CSRF-Token": csrfToken() },
            }
        );

        if (response.status === 401) {
            window.location.assign("/login");
            return;
        }

        const data = await response.json().catch(() => null);
        if (!response.ok || !data) {
            showLocalResult(card, extractErrorMessage(data), true);
            button.disabled = false;
            button.textContent = originalText;
            return;
        }

        showLocalResult(card, data.message || "本地作业已完成", false);
        setLocalTaskCompleted(card, true);
    } catch (error) {
        showLocalResult(card, "网络异常，请确认服务是否在运行", true);
        button.disabled = false;
        button.textContent = originalText;
    }
}

function setLocalTaskCompleted(card, completed) {
    card.classList.toggle("is-accepted", completed);
    setExerciseStateBadge(card, completed ? "accepted" : "redoing");

    const completeButton = card.querySelector("[data-complete-exercise]");
    const resetButton = card.querySelector("[data-reset-local]");
    const hint = card.querySelector(".exercise-hint");
    const resultBox = card.querySelector("[data-local-result]");

    if (completeButton) {
        completeButton.hidden = completed;
        completeButton.disabled = false;
        completeButton.textContent = "标记完成";
    }
    if (resetButton) {
        resetButton.hidden = !completed;
        resetButton.disabled = false;
    }
    if (hint) {
        hint.textContent = completed
            ? "已完成，可重新练习"
            : "完成后点击标记完成";
    }
    if (resultBox) {
        resultBox.hidden = true;
        resultBox.replaceChildren();
    }
}

function showLocalResult(card, message, isError) {
    const box = card.querySelector("[data-local-result]");
    if (!box) {
        return;
    }

    box.hidden = false;
    box.className = `exercise-result is-${isError ? "error" : "accepted"}`;
    box.replaceChildren();

    const title = document.createElement("strong");
    title.className = "result-title";
    title.textContent = isError ? "操作失败" : "已完成";

    const text = document.createElement("p");
    text.className = "result-message";
    text.textContent = message;

    box.append(title, text);
}

// ---------- 练习提交 ----------

const RESULT_LABELS = {
    accepted: "通过",
    wrong_answer: "答案错误",
    timeout: "运行超时",
    runtime_error: "运行错误",
    internal_error: "服务异常",
};

document.addEventListener("submit", async (event) => {
    if (!(event.target instanceof Element)) {
        return;
    }

    const form = event.target.closest(".exercise-form");
    if (!form) {
        return;
    }

    event.preventDefault();
    await submitExercise(form);
});

// 已通过的练习可以点击「重做」重新解锁表单；保留上次作答，便于修改。
document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) {
        return;
    }

    const button = event.target.closest("[data-redo-exercise]");
    if (!button) {
        return;
    }

    const card = button.closest(".exercise-card");
    const form = card ? card.querySelector(".exercise-form") : null;
    if (!card || !form) {
        return;
    }

    setExerciseLocked(card, form, false);
    setExerciseStateBadge(card, "redoing");

    const resultBox = form.querySelector("[data-result]");
    if (resultBox) {
        resultBox.hidden = true;
        resultBox.replaceChildren();
    }

    const firstInput = form.querySelector("input, textarea");
    if (firstInput) {
        firstInput.focus();
    }
});

// 在代码框中按 Tab 插入 4 个空格，避免焦点跳出编辑器。
document.addEventListener("keydown", (event) => {
    if (
        event.key !== "Tab" ||
        !(event.target instanceof HTMLTextAreaElement) ||
        !event.target.classList.contains("code-input")
    ) {
        return;
    }

    event.preventDefault();
    const textarea = event.target;
    textarea.setRangeText(
        "    ",
        textarea.selectionStart,
        textarea.selectionEnd,
        "end"
    );
});

async function submitExercise(form) {
    const exerciseId = form.dataset.exerciseId;
    const exerciseType = form.dataset.exerciseType;
    const button = form.querySelector('button[type="submit"]');
    const resultBox = form.querySelector("[data-result]");
    if (!exerciseId || !button || !resultBox) {
        return;
    }

    const payload = {};
    if (exerciseType === "single_choice") {
        const selected = form.querySelector('input[name="answer_index"]:checked');
        if (!selected) {
            showResult(resultBox, "error", "请先选择一个选项");
            return;
        }
        payload.answer_index = Number(selected.value);
    } else if (exerciseType === "fill_blank") {
        const input = form.querySelector('input[name="answer"]');
        if (!input || !input.value.trim()) {
            showResult(resultBox, "error", "请先填写答案");
            return;
        }
        payload.answer = input.value;
    } else if (exerciseType === "trajectory_task") {
        const input = form.querySelector('textarea[name="trajectory"]');
        if (!input || !input.value.trim()) {
            showResult(resultBox, "error", "请先粘贴轨迹 JSON");
            return;
        }
        try {
            payload.trajectory = JSON.parse(input.value);
        } catch (error) {
            showResult(
                resultBox,
                "error",
                "轨迹 JSON 格式不正确，请检查逗号、引号和括号。"
            );
            return;
        }
    } else {
        const codeInput = form.querySelector('textarea[name="code"]');
        if (!codeInput || !codeInput.value.trim()) {
            showResult(resultBox, "error", "请先编写代码");
            return;
        }
        payload.code = codeInput.value;
    }

    setLoading(button, true);
    showResult(resultBox, "loading", "判题中，请稍候…");

    try {
        const response = await fetch(
            `/api/exercises/${encodeURIComponent(exerciseId)}/submit`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRF-Token": csrfToken(),
                },
                credentials: "same-origin",
                body: JSON.stringify(payload),
            }
        );

        if (response.status === 401) {
            window.location.assign("/login");
            return;
        }

        const data = await response.json().catch(() => null);
        if (!response.ok || !data) {
            showResult(resultBox, "error", extractErrorMessage(data));
            return;
        }

        renderResult(resultBox, data);
    } catch (error) {
        showResult(resultBox, "error", "网络异常，请确认服务是否在运行");
    } finally {
        setLoading(button, false);
    }
}

function extractErrorMessage(data) {
    if (!data) {
        return "提交失败，请稍后重试";
    }
    if (typeof data.message === "string") {
        return data.message;
    }
    if (typeof data.detail === "string") {
        return data.detail;
    }
    return "提交数据格式不正确";
}

function ensureExerciseStateBadge(card) {
    let badge = card.querySelector(".exercise-state");
    if (badge) {
        return badge;
    }

    const row = document.createElement("p");
    row.className = "exercise-state-row";
    badge = document.createElement("span");
    badge.className = "exercise-state";
    row.appendChild(badge);

    const header = card.querySelector(".exercise-head");
    if (header) {
        header.insertAdjacentElement("afterend", row);
    } else {
        card.prepend(row);
    }
    return badge;
}

function setExerciseStateBadge(card, status) {
    const isLocal = card.dataset.exerciseType === "local_task";
    const isTrajectory = card.dataset.exerciseType === "trajectory_task";
    const labels = {
        accepted: isLocal ? "已完成" : "已通过",
        wrong_answer: isTrajectory
            ? "轨迹未通过 · 可继续重做"
            : "答案错误 · 可继续重做",
        timeout: "运行超时 · 可继续重做",
        runtime_error: "运行错误 · 可继续重做",
        redoing: isLocal ? "重新练习中" : "重新作答中",
    };
    const badge = ensureExerciseStateBadge(card);
    badge.className = `exercise-state is-${status}`;
    badge.textContent = labels[status] || "可继续重做";
}

function setExerciseLocked(card, form, locked) {
    form.querySelectorAll("input, textarea").forEach((input) => {
        if (input instanceof HTMLTextAreaElement) {
            input.readOnly = locked;
        } else {
            input.disabled = locked;
        }
    });

    const submitButton = form.querySelector('button[type="submit"]');
    const redoButton = form.querySelector("[data-redo-exercise]");
    const hint = form.querySelector(".exercise-hint");

    if (submitButton) {
        submitButton.hidden = locked;
        submitButton.disabled = false;
    }
    if (redoButton) {
        redoButton.hidden = !locked;
        redoButton.disabled = false;
    }
    if (hint) {
        const isTrajectory = card.dataset.exerciseType === "trajectory_task";
        hint.textContent = locked
            ? "本题已通过，点击重做可再次练习"
            : isTrajectory
              ? "提交后检查轨迹规则"
              : "提交后立即判题";
    }

    card.classList.toggle("is-accepted", locked);
}

function renderResult(box, data) {
    box.hidden = false;
    box.className = `exercise-result is-${data.status}`;
    box.replaceChildren();

    const title = document.createElement("strong");
    title.className = "result-title";
    title.textContent = RESULT_LABELS[data.status] || data.status;
    box.appendChild(title);

    const message = document.createElement("p");
    message.className = "result-message";
    message.textContent = data.message || "";
    box.appendChild(message);

    if (Array.isArray(data.test_results) && data.test_results.length > 0) {
        const list = document.createElement("ul");
        list.className = "test-list";
        data.test_results.forEach((testCase) => {
            list.appendChild(renderTestCase(testCase));
        });
        box.appendChild(list);
    }

    if (Array.isArray(data.rule_results) && data.rule_results.length > 0) {
        const list = document.createElement("ul");
        list.className = "rule-list";
        data.rule_results.forEach((rule) => {
            const item = document.createElement("li");
            item.className = `rule-row ${rule.passed ? "is-passed" : "is-failed"}`;

            const status = document.createElement("span");
            status.className = "rule-status";
            status.textContent = rule.passed ? "通过" : "失败";

            const label = document.createElement("span");
            label.className = "rule-label";
            label.textContent = rule.label || rule.rule || "规则";

            const detail = document.createElement("span");
            detail.className = "rule-detail";
            detail.textContent = rule.detail || "";

            item.append(status, label, detail);
            list.appendChild(item);
        });
        box.appendChild(list);
    }

    if (data.lesson_completed) {
        const note = document.createElement("p");
        note.className = "result-note";
        note.textContent = "本课练习已全部通过，学习进度已更新。";
        box.appendChild(note);
    }

    // 通过后锁定作答并显示「重做」；错误或异常则保持可编辑。
    const card = box.closest(".exercise-card");
    const form = card ? card.querySelector(".exercise-form") : null;
    if (card && form) {
        if (data.status === "accepted") {
            setExerciseLocked(card, form, true);
            setExerciseStateBadge(card, "accepted");
        } else if (
            ["wrong_answer", "timeout", "runtime_error"].includes(data.status)
        ) {
            setExerciseLocked(card, form, false);
            setExerciseStateBadge(card, data.status);
        }
    }
}

function renderTestCase(testCase) {
    const item = document.createElement("li");
    item.className = `test-row is-${testCase.status}`;

    const head = document.createElement("div");
    head.className = "test-head";

    const label = document.createElement("span");
    label.textContent = `用例 ${testCase.index}`;

    const status = document.createElement("span");
    status.textContent = `${RESULT_LABELS[testCase.status] || testCase.status} · ${testCase.duration_ms}ms`;

    head.append(label, status);
    item.appendChild(head);

    if (testCase.status === "wrong_answer") {
        const expected = document.createElement("p");
        expected.textContent = "期望：";
        const expectedCode = document.createElement("code");
        expectedCode.textContent = testCase.expected_stdout;
        expected.appendChild(expectedCode);

        const actual = document.createElement("p");
        actual.textContent = "实际：";
        const actualCode = document.createElement("code");
        actualCode.textContent = testCase.actual_stdout || "（无输出）";
        actual.appendChild(actualCode);

        item.append(expected, actual);
    }

    if (testCase.status === "runtime_error" && testCase.stderr) {
        const stderr = document.createElement("pre");
        stderr.className = "test-stderr";
        stderr.textContent = testCase.stderr;
        item.appendChild(stderr);
    }

    if (testCase.status === "timeout") {
        const timeoutNote = document.createElement("p");
        timeoutNote.textContent = "程序未在限定时间内结束，请检查是否有死循环。";
        item.appendChild(timeoutNote);
    }

    // 每个用例都可以展开查看输入与期望输出；答案错误时已在上方展示期望/实际。
    const detail = document.createElement("details");
    detail.className = "testcase-detail";

    const summary = document.createElement("summary");
    summary.textContent =
        testCase.status === "wrong_answer" ? "查看输入" : "查看输入与期望输出";
    detail.appendChild(summary);

    const input = document.createElement("p");
    input.textContent = "输入：";
    const inputCode = document.createElement("code");
    inputCode.textContent = testCase.stdin || "（无输入）";
    input.appendChild(inputCode);
    detail.appendChild(input);

    if (testCase.status !== "wrong_answer") {
        const expected = document.createElement("p");
        expected.textContent = "期望：";
        const expectedCode = document.createElement("code");
        expectedCode.textContent = testCase.expected_stdout;
        expected.appendChild(expectedCode);
        detail.appendChild(expected);
    }

    item.appendChild(detail);
    return item;
}

// ---------- 轨迹预览 ----------

document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) {
        return;
    }

    const button = event.target.closest("[data-preview-trajectory]");
    if (!button) {
        return;
    }

    const card = button.closest(".exercise-card");
    if (card) {
        renderTrajectoryView(card);
    }
});

function renderTrajectoryView(card) {
    const textarea = card.querySelector('textarea[name="trajectory"]');
    const view = card.querySelector("[data-trajectory-view]");
    if (!textarea || !view) {
        return;
    }

    view.replaceChildren();
    const raw = textarea.value.trim();
    if (!raw) {
        view.hidden = true;
        return;
    }

    let data;
    try {
        data = JSON.parse(raw);
    } catch (error) {
        view.hidden = false;
        const message = document.createElement("p");
        message.className = "trajectory-error";
        message.textContent = `JSON 格式不正确：${error.message}`;
        view.appendChild(message);
        return;
    }

    if (!data || typeof data !== "object" || !Array.isArray(data.steps)) {
        view.hidden = false;
        const message = document.createElement("p");
        message.className = "trajectory-error";
        message.textContent = "轨迹需要包含 steps 数组。";
        view.appendChild(message);
        return;
    }

    view.hidden = false;

    const toolCalls = data.steps.filter(
        (step) => step && typeof step === "object" && step.type === "action"
    ).length;
    const summary = document.createElement("p");
    summary.className = "trajectory-summary";
    summary.textContent = `共 ${data.steps.length} 步，工具调用 ${toolCalls} 次${
        data.final_answer ? " · 已有最终答案" : ""
    }`;
    view.appendChild(summary);

    const list = document.createElement("ol");
    list.className = "trajectory-steps";
    const labels = {
        thought: "思考",
        action: "行动",
        observation: "观察",
        finish: "完成",
        error: "错误",
    };

    data.steps.forEach((rawStep, index) => {
        const step =
            rawStep && typeof rawStep === "object" ? rawStep : {};
        const item = document.createElement("li");
        item.className = `trajectory-step is-${step.type || "unknown"}`;

        const head = document.createElement("div");
        head.className = "trajectory-step-head";

        const number = document.createElement("span");
        number.className = "trajectory-step-index";
        number.textContent = String(index + 1);

        const type = document.createElement("span");
        type.className = "trajectory-step-type";
        type.textContent = labels[step.type] || step.type || "未知";

        head.append(number, type);
        item.appendChild(head);

        const body = document.createElement("div");
        body.className = "trajectory-step-body";

        if (step.type === "action") {
            const tool = document.createElement("code");
            tool.textContent = step.tool || "（未命名工具）";
            body.appendChild(tool);

            if (step.arguments && typeof step.arguments === "object") {
                const args = document.createElement("pre");
                args.textContent = JSON.stringify(step.arguments, null, 2);
                body.appendChild(args);
            }
        } else {
            const text = document.createElement("p");
            text.textContent = step.content || "（空）";
            body.appendChild(text);
        }

        item.appendChild(body);
        list.appendChild(item);
    });

    view.appendChild(list);
}

function showResult(box, status, message) {
    box.hidden = false;
    box.className = `exercise-result is-${status}`;
    box.replaceChildren();

    const title = document.createElement("strong");
    title.className = "result-title";
    title.textContent = status === "loading" ? "判题中" : "提交失败";
    box.appendChild(title);

    const text = document.createElement("p");
    text.className = "result-message";
    text.textContent = message;
    box.appendChild(text);
}

function setLoading(button, loading) {
    if (!button.dataset.originalText) {
        button.dataset.originalText = button.textContent.trim();
    }
    button.disabled = loading;
    button.textContent = loading ? "判题中…" : button.dataset.originalText;
}

// 所有事件监听器就绪后再启用按钮，避免 JS 未就绪时产生无效提交。
document.querySelectorAll(".exercise-form button[type='submit']").forEach((button) => {
    button.disabled = false;
});

document.querySelectorAll("[data-complete-lesson]").forEach((button) => {
    button.disabled = false;
});

document.querySelectorAll("[data-redo-exercise]").forEach((button) => {
    button.disabled = false;
});

document.querySelectorAll("[data-complete-exercise], [data-reset-local]").forEach(
    (button) => {
        button.disabled = false;
    }
);

document.querySelectorAll("[data-preview-trajectory]").forEach((button) => {
    button.disabled = false;
});

document
    .querySelectorAll('.exercise-card[data-exercise-type="trajectory_task"]')
    .forEach((card) => {
        renderTrajectoryView(card);
    });
