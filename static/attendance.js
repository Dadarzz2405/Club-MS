document.addEventListener("DOMContentLoaded", () => {
    const sessionSelect = document.getElementById("sessionSelect");
    const downloadLink = document.getElementById("download-link");

    sessionSelect.addEventListener("change", () => {
        const sessionId = sessionSelect.value;
        if (sessionId) {
            downloadLink.href = `/export/attendance/${sessionId}`;
            downloadLink.removeAttribute("disabled");
        } else {
            downloadLink.href = "#";
            downloadLink.setAttribute("disabled", "true");
        }
    });

    document.querySelectorAll(".att-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            if (btn.disabled) return;

            const userId = btn.dataset.userId;
            const status = btn.dataset.status;
            const sessionId = sessionSelect.value;

            if (!sessionId) {
                alert("Select a session first.");
                return;
            }

            btn.disabled = true;

            try {
                const res = await fetch("/api/attendance", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        user_id: userId,
                        session_id: sessionId,
                        status: status
                    })
                });

                const data = await res.json();

                if (res.ok && data.success) {
                    lockRow(userId, status);
                    return;
                }

                // Handle known backend errors
                if (data.error === "already_marked") {
                    lockRow(userId, status);
                    return;
                }

                if (data.error === "session_locked") {
                    alert("This session is locked.");
                } else if (data.error === "forbidden") {
                    alert("You do not have permission to mark attendance.");
                } else {
                    alert("Failed to save attendance.");
                }

                btn.disabled = false;

            } catch (err) {
                btn.disabled = false;
                alert("Network error.");
            }
        });
    });
});

function lockRow(userId, activeStatus) {
    document.querySelectorAll(`[data-user-id="${userId}"]`).forEach(btn => {
        btn.disabled = true;

        btn.classList.remove(
            "btn-outline-success",
            "btn-outline-danger",
            "btn-outline-warning"
        );

        if (btn.dataset.status === activeStatus) {
            btn.classList.add("btn-secondary");
        }
    });
}
