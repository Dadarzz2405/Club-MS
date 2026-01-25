document.addEventListener("DOMContentLoaded", () => {
    const sessionSelect = document.getElementById("sessionSelect");
    const downloadLink = document.getElementById("download-link");
    const lockButton = document.getElementById("lock-session-btn");
    const lockStatus = document.getElementById("lock-status");

    async function checkSessionLock(sessionId) {
        try {
            const res = await fetch(`/api/session/${sessionId}/status`);
            const data = await res.json();
            
            if (data.is_locked) {
                // Disable all attendance buttons
                document.querySelectorAll(".att-btn").forEach(btn => {
                    btn.disabled = true;
                    btn.classList.add('disabled');
                });
                
                if (lockStatus) {
                    lockStatus.innerHTML = '<span class="badge bg-danger"><i class="fas fa-lock me-1"></i>Session Locked</span>';
                }
                
                if (lockButton) {
                    lockButton.disabled = true;
                    lockButton.innerHTML = '<i class="fas fa-lock me-2"></i>Locked';
                }
            } else {
                // Enable all attendance buttons
                document.querySelectorAll(".att-btn").forEach(btn => {
                    btn.disabled = false;
                    btn.classList.remove('disabled');
                });
                
                if (lockStatus) {
                    lockStatus.innerHTML = '<span class="badge bg-success"><i class="fas fa-unlock me-1"></i>Session Open</span>';
                }
                
                if (lockButton) {
                    lockButton.disabled = false;
                    lockButton.innerHTML = '<i class="fas fa-lock me-2"></i>Lock Session';
                }
            }
            
            return data.is_locked;
        } catch (err) {
            console.error("Error checking lock status:", err);
            return false;
        }
    }

    sessionSelect.addEventListener("change", async () => {
        const sessionId = sessionSelect.value;
        if (sessionId) {
            downloadLink.href = `/export/attendance/${sessionId}`;
            downloadLink.removeAttribute("disabled");
            
            // Check if session is locked
            await checkSessionLock(sessionId);
        } else {
            downloadLink.href = "#";
            downloadLink.setAttribute("disabled", "true");
            
            if (lockStatus) {
                lockStatus.innerHTML = '';
            }
        }
    });

    // Lock session button handler
    if (lockButton) {
        lockButton.addEventListener("click", async () => {
            const sessionId = sessionSelect.value;
            
            if (!sessionId) {
                alert("Please select a session first.");
                return;
            }
            
            if (!confirm("Are you sure you want to lock this session? This will prevent any further attendance marking.")) {
                return;
            }
            
            lockButton.disabled = true;
            lockButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Locking...';
            
            try {
                const res = await fetch(`/api/session/${sessionId}/lock`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    }
                });
                
                if (res.ok) {
                    await checkSessionLock(sessionId);
                    alert("Session locked successfully!");
                } else {
                    const data = await res.json();
                    alert(data.error || "Failed to lock session.");
                    lockButton.disabled = false;
                    lockButton.innerHTML = '<i class="fas fa-lock me-2"></i>Lock Session';
                }
            } catch (err) {
                console.error("Error locking session:", err);
                alert("Network error while locking session.");
                lockButton.disabled = false;
                lockButton.innerHTML = '<i class="fas fa-lock me-2"></i>Lock Session';
            }
        });
    }

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
    
    // Check initial lock status if session is pre-selected
    if (sessionSelect.value) {
        checkSessionLock(sessionSelect.value);
    }
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