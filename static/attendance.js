document.addEventListener("DOMContentLoaded", () => {
    const sessionSelect = document.getElementById("sessionSelect");
    const downloadLink = document.getElementById("download-link");
    const lockButton = document.getElementById("lock-session-btn");
    const lockStatus = document.getElementById("lock-status");

    console.log("Attendance.js loaded");
    console.log("Session select:", sessionSelect);
    console.log("Download link:", downloadLink);

    async function checkSessionLock(sessionId) {
        try {
            const res = await fetch(`/api/session/${sessionId}/status`);
            const data = await res.json();
            
            if (data.is_locked) {
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
                    lockButton.style.display = 'inline-block';
                }
            }
            
            return data.is_locked;
        } catch (err) {
            console.error("Error checking lock status:", err);
            return false;
        }
    }

    if (sessionSelect) {
        sessionSelect.addEventListener("change", async () => {
            const sessionId = sessionSelect.value;
            console.log("Session changed to:", sessionId);
            
            if (sessionId && downloadLink) {
                const downloadUrl = `/export/attendance/${sessionId}`;
                console.log("Setting download URL to:", downloadUrl);
                
                downloadLink.href = downloadUrl;
                downloadLink.removeAttribute("disabled");
                downloadLink.classList.remove("disabled");
                
                downloadLink.style.pointerEvents = "auto";
                downloadLink.style.opacity = "1";
                
                console.log("Download link enabled");
                
                await checkSessionLock(sessionId);
            } else if (downloadLink) {
                downloadLink.href = "#";
                downloadLink.setAttribute("disabled", "true");
                downloadLink.classList.add("disabled");
                downloadLink.style.pointerEvents = "none";
                downloadLink.style.opacity = "0.6";
                
                if (lockStatus) {
                    lockStatus.innerHTML = '';
                }
                
                if (lockButton) {
                    lockButton.style.display = 'none';
                }
            }
        });
    } else {
        console.warn("Session select element not found");
    }

    // Lock session button handler
    if (lockButton) {
        lockButton.addEventListener("click", async () => {
            if (!sessionSelect) return;
            
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

    // Attendance button handlers
    document.querySelectorAll(".att-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            if (btn.disabled) return;

            const userId = btn.dataset.userId;
            const status = btn.dataset.status;
            const sessionId = sessionSelect ? sessionSelect.value : null;

            if (!sessionId) {
                alert("Select a session first.");
                return;
            }

            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

            try {
                const endpoint = document.querySelector('[data-attendance-type="core"]') 
                    ? "/api/attendance/core" 
                    : "/api/attendance";

                const res = await fetch(endpoint, {
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
                    btn.innerHTML = '<i class="fas fa-check"></i>';
                    setTimeout(() => {
                        btn.innerHTML = getButtonIcon(status);
                    }, 1000);
                    return;
                }

                if (data.error === "already_marked") {
                    lockRow(userId, status);
                    btn.innerHTML = '<i class="fas fa-check"></i>';
                    alert("This attendance was already marked.");
                    return;
                }

                if (data.error === "session_locked") {
                    alert("This session is locked.");
                } else if (data.error === "forbidden") {
                    alert("You do not have permission to mark attendance.");
                } else {
                    alert("Failed to save attendance: " + (data.error || "Unknown error"));
                }

                btn.disabled = false;
                btn.innerHTML = getButtonIcon(status);

            } catch (err) {
                console.error("Attendance error:", err);
                btn.disabled = false;
                btn.innerHTML = getButtonIcon(status);
                alert("Network error. Please try again.");
            }
        });
    });
    
    // Initialize on page load if session is already selected
    if (sessionSelect && sessionSelect.value) {
        const sessionId = sessionSelect.value;
        checkSessionLock(sessionId);
        
        if (downloadLink) {
            const downloadUrl = `/export/attendance/${sessionId}`;
            downloadLink.href = downloadUrl;
            downloadLink.removeAttribute("disabled");
            downloadLink.classList.remove("disabled");
            downloadLink.style.pointerEvents = "auto";
            downloadLink.style.opacity = "1";
        }
    }
});

function getButtonIcon(status) {
    const icons = {
        'present': '<i class="fas fa-check"></i> P',
        'absent': '<i class="fas fa-times"></i> A',
        'excused': '<i class="fas fa-exclamation"></i> E',
        'late': '<i class="fas fa-clock"></i> L'
    };
    return icons[status] || status;
}

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