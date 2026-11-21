/**
 * CivicResolve - Citizen Interactive Client Scripts
 */

document.addEventListener("DOMContentLoaded", () => {
    initThemeToggle();
    initDemoAutofillChips();
    initGeolocation();
    initImageUploadPreview();
    initAIPreview();
    initLiveSearch();
    initUpvoteButtons();
});

/**
 * 1. Accessible Light / Dark Theme Toggle
 */
function initThemeToggle() {
    const toggleBtn = document.getElementById("theme-toggle");
    if (!toggleBtn) return;

    const darkIcon = document.getElementById("theme-toggle-dark-icon");
    const lightIcon = document.getElementById("theme-toggle-light-icon");

    function updateIcons(isDark) {
        if (darkIcon && lightIcon) {
            if (isDark) {
                darkIcon.classList.add("hidden");
                lightIcon.classList.remove("hidden");
            } else {
                darkIcon.classList.remove("hidden");
                lightIcon.classList.add("hidden");
            }
        }
    }

    // Initial icon state
    updateIcons(document.documentElement.classList.contains("dark"));

    toggleBtn.addEventListener("click", () => {
        const isDark = document.documentElement.classList.toggle("dark");
        localStorage.setItem("theme", isDark ? "dark" : "light");
        updateIcons(isDark);
    });
}

/**
 * 2. One-Click Demo Autofill Chips for Rapid Testing
 */
function initDemoAutofillChips() {
    const chipWater = document.getElementById("demo-chip-water");
    const chipLight = document.getElementById("demo-chip-light");
    const chipPothole = document.getElementById("demo-chip-pothole");

    const titleInput = document.getElementById("title");
    const descInput = document.getElementById("description");
    const locInput = document.getElementById("location-input");
    const catInput = document.getElementById("user_category");
    const formCard = document.getElementById("reporting-form-card");

    const autofill = (title, desc, loc, cat) => {
        if (titleInput) titleInput.value = title;
        if (descInput) descInput.value = desc;
        if (locInput) locInput.value = loc;
        if (catInput) catInput.value = cat;

        if (formCard) {
            formCard.scrollIntoView({ behavior: "smooth", block: "start" });
            formCard.classList.add("ring-2", "ring-primary-500", "ring-offset-2");
            setTimeout(() => {
                formCard.classList.remove("ring-2", "ring-primary-500", "ring-offset-2");
            }, 1200);
        }
    };

    if (chipWater) {
        chipWater.addEventListener("click", () => {
            autofill(
                "High-pressure water distribution pipe burst flooding neighborhood crossing",
                "A major municipal potable water main has ruptured near the junction. Water is gushing violently across the pedestrian walkway, causing heavy erosion and beginning to inundate several ground-floor shops and homes.",
                "Avinashi Road, Near PSG Tech Pedestrian Underpass, Peelamedu, Coimbatore",
                "Water & Drainage"
            );
        });
    }

    if (chipLight) {
        chipLight.addEventListener("click", () => {
            autofill(
                "Open electrical junction box sparking continuously on streetlight pole #47",
                "Streetlight inspection cover is completely broken and frayed 230V live cables are sparking vigorously in the damp rain. The adjacent walkway is in total darkness, presenting an immediate electrocution hazard to pedestrians.",
                "Crosscut Road, Near Gandhipuram 4th Street Corner, Coimbatore",
                "Streetlights & Electrical"
            );
        });
    }

    if (chipPothole) {
        chipPothole.addEventListener("click", () => {
            autofill(
                "Dangerous deep crater-sized pothole on main arterial transit lane",
                "A dangerous crater measuring 3 feet wide and 9 inches deep with sharp jagged asphalt has formed right before the bus bay. Multiple two-wheelers have skidded and damaged their rims today during peak morning traffic.",
                "Mettupalayam Road, Near Saibaba Colony Signal, Coimbatore",
                "Roads & Infrastructure"
            );
        });
    }
}

/**
 * 3. HTML5 Geolocation Support
 */
function initGeolocation() {
    const geoBtn = document.getElementById("btn-geolocation");
    const locInput = document.getElementById("location-input");
    const latInput = document.getElementById("latitude-input");
    const lngInput = document.getElementById("longitude-input");
    const geoStatus = document.getElementById("geo-status");

    if (!geoBtn || !locInput) return;

    geoBtn.addEventListener("click", () => {
        if (!navigator.geolocation) {
            alert("Geolocation is not supported by your browser.");
            return;
        }

        const originalText = geoBtn.innerHTML;
        geoBtn.innerHTML = `
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-600 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
            </svg> Detecting GPS...
        `;
        geoBtn.disabled = true;

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = pos.coords.latitude.toFixed(5);
                const lng = pos.coords.longitude.toFixed(5);
                
                if (latInput) latInput.value = lat;
                if (lngInput) lngInput.value = lng;

                locInput.value = `GPS (${lat}, ${lng}) - Near PSG iTech Corridor`;
                if (geoStatus) {
                    geoStatus.textContent = `✓ Exact GPS captured (Accuracy: ±${Math.round(pos.coords.accuracy)}m)`;
                    geoStatus.className = "text-xs text-emerald-600 dark:text-emerald-400 font-medium mt-1";
                }

                geoBtn.innerHTML = originalText;
                geoBtn.disabled = false;
            },
            (err) => {
                console.warn("Geolocation error:", err.message);
                if (geoStatus) {
                    geoStatus.textContent = "Unable to retrieve GPS automatically. Please enter your landmark manually.";
                    geoStatus.className = "text-xs text-amber-600 dark:text-amber-400 font-medium mt-1";
                }
                geoBtn.innerHTML = originalText;
                geoBtn.disabled = false;
            },
            { timeout: 10000, enableHighAccuracy: true }
        );
    });
}

/**
 * 4. Lightweight Image Upload & Preview
 */
function initImageUploadPreview() {
    const fileInput = document.getElementById("image-upload");
    const previewContainer = document.getElementById("image-preview-container");
    const previewImg = document.getElementById("image-preview-img");
    const removeBtn = document.getElementById("image-remove-btn");
    const uploadPrompt = document.getElementById("upload-prompt");

    if (!fileInput || !previewContainer || !previewImg) return;

    fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // Size check (max 3MB)
        if (file.size > 3 * 1024 * 1024) {
            alert("Please select an image smaller than 3MB to keep the application lightweight.");
            fileInput.value = "";
            return;
        }

        const reader = new FileReader();
        reader.onload = (event) => {
            previewImg.src = event.target.result;
            previewContainer.classList.remove("hidden");
            if (uploadPrompt) uploadPrompt.classList.add("hidden");
        };
        reader.readAsDataURL(file);
    });

    if (removeBtn) {
        removeBtn.addEventListener("click", () => {
            fileInput.value = "";
            previewImg.src = "";
            previewContainer.classList.add("hidden");
            if (uploadPrompt) uploadPrompt.classList.remove("hidden");
        });
    }
}

/**
 * 5. Real-time Gemini AI Preview with Neural Scanning Shimmer
 */
function initAIPreview() {
    const btnPreview = document.getElementById("btn-ai-preview");
    const titleInput = document.getElementById("title");
    const descInput = document.getElementById("description");
    const catInput = document.getElementById("user_category");
    const locInput = document.getElementById("location-input");
    const previewBox = document.getElementById("ai-preview-box");
    const previewContent = document.getElementById("ai-preview-content");
    const formCard = document.getElementById("reporting-form-card");

    if (!btnPreview || !titleInput || !descInput || !previewBox || !previewContent) return;

    btnPreview.addEventListener("click", async () => {
        const title = titleInput.value.trim();
        const description = descInput.value.trim();
        const user_category = catInput ? catInput.value : "";
        const location = locInput ? locInput.value.trim() : "";

        if (title.length < 5 || description.length < 10) {
            alert("Please write at least a basic title and description before requesting AI classification.");
            return;
        }

        const originalBtnHtml = btnPreview.innerHTML;
        btnPreview.innerHTML = `
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-purple-600 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
            </svg> Neural Triage Scanning...
        `;
        btnPreview.disabled = true;

        if (formCard) formCard.classList.add("neural-scanner");

        // Check if image preview has data
        const previewImg = document.getElementById("image-preview-img");
        let imageData = null;
        if (previewImg && previewImg.src && previewImg.src.startsWith("data:")) {
            imageData = previewImg.src;
        }

        try {
            const resp = await fetch("/api/classify", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title,
                    description,
                    user_category,
                    location,
                    image_data: imageData
                })
            });

            if (!resp.ok) throw new Error("Classification request failed");

            const data = await resp.json();

            // Color badge lookup matching warm terracotta, ochre, and forest sage palette
            let priorityBadge = "bg-[#FAF0E6] dark:bg-stone-800 text-[#C84B31] dark:text-[#E06D53] border-[#F2D7CE] dark:border-stone-700";
            if (data.priority === "Critical") priorityBadge = "bg-rose-100 dark:bg-rose-950/70 text-rose-800 dark:text-rose-200 border-rose-300 dark:border-rose-800 badge-critical-pulse";
            if (data.priority === "High") priorityBadge = "bg-amber-100 dark:bg-amber-950/70 text-amber-900 dark:text-amber-200 border-amber-300 dark:border-amber-800";
            if (data.priority === "Low") priorityBadge = "bg-emerald-50 dark:bg-emerald-950/70 text-emerald-800 dark:text-emerald-200 border-emerald-200 dark:border-emerald-800";

            previewContent.innerHTML = `
                <div class="space-y-3">
                    <div class="flex flex-wrap items-center gap-2">
                        <span class="px-2.5 py-1 text-xs font-semibold rounded-full border ${priorityBadge}">
                            Priority: ${data.priority}
                        </span>
                        <span class="px-2.5 py-1 text-xs font-medium rounded-full bg-[#FAF7F2] dark:bg-stone-800 text-stone-800 dark:text-stone-200 border border-[#E5DEC9] dark:border-stone-700">
                            Category: ${data.category}
                        </span>
                        <span class="px-2.5 py-1 text-xs font-bold rounded-full bg-[#FAF0E6] dark:bg-stone-800 text-[#C84B31] dark:text-[#E06D53] border border-[#F2D7CE] dark:border-stone-700">
                            ⏱️ Target SLA: ${data.sla_target || '24 Hours'}
                        </span>
                        <span class="text-xs text-[#C84B31] dark:text-[#E06D53] bg-[#FAF0E6] dark:bg-stone-800 px-2.5 py-1 rounded-full border border-[#F2D7CE] dark:border-stone-700 font-medium">
                            ⚡ ${data.engine || "Gemini 2.5 Flash"}
                        </span>
                    </div>
                    <div>
                        <p class="text-xs font-semibold text-stone-500 dark:text-stone-400 uppercase tracking-wider">Recommended Civic Department</p>
                        <p class="text-sm font-medium text-[#1C1917] dark:text-[#F5F2EB]">${data.department}</p>
                    </div>
                    <div>
                        <p class="text-xs font-semibold text-stone-500 dark:text-stone-400 uppercase tracking-wider">AI Executive Summary</p>
                        <p class="text-sm text-stone-800 dark:text-stone-200 bg-white dark:bg-[#161513] p-2.5 rounded-lg border border-[#E5DEC9] dark:border-stone-700">${data.ai_summary}</p>
                    </div>
                    <div>
                        <p class="text-xs font-semibold text-stone-500 dark:text-stone-400 uppercase tracking-wider">Urgency Assessment</p>
                        <p class="text-xs text-stone-600 dark:text-stone-400">${data.urgency_reason}</p>
                    </div>
                </div>
            `;
            previewBox.classList.remove("hidden");
            previewBox.scrollIntoView({ behavior: "smooth", block: "nearest" });

        } catch (err) {
            console.error("AI Preview Error:", err);
            alert("Could not complete AI preview. You can still submit the form and it will be processed automatically.");
        } finally {
            if (formCard) formCard.classList.remove("neural-scanner");
            btnPreview.innerHTML = originalBtnHtml;
            btnPreview.disabled = false;
        }
    });
}

/**
 * 6. Client-side Live Filtering for Issue Tracker
 */
function initLiveSearch() {
    const searchInput = document.getElementById("tracker-live-search");
    const complaintCards = document.querySelectorAll(".complaint-card");

    if (!searchInput || complaintCards.length === 0) return;

    searchInput.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase().trim();
        let matchCount = 0;

        complaintCards.forEach((card) => {
            const text = card.textContent.toLowerCase();
            if (text.includes(query)) {
                card.style.display = "";
                matchCount++;
            } else {
                card.style.display = "none";
            }
        });

        const noResultsMsg = document.getElementById("no-filter-results");
        if (noResultsMsg) {
            noResultsMsg.classList.toggle("hidden", matchCount > 0);
        }
    });
}

/**
 * 7. Community Impact Upvote / Duplicate Awareness (+1 Confirm Issue)
 */
function initUpvoteButtons() {
    document.querySelectorAll(".btn-upvote").forEach((btn) => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            const ticketId = btn.getAttribute("data-ticket-id");
            if (!ticketId || btn.disabled) return;

            const countEl = btn.querySelector(".upvote-count");
            const originalHtml = btn.innerHTML;
            btn.disabled = true;

            try {
                const resp = await fetch(`/api/complaints/${ticketId}/upvote`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" }
                });

                if (!resp.ok) throw new Error("Upvote failed");

                const result = await resp.json();
                if (countEl) {
                    countEl.textContent = result.upvotes;
                    countEl.classList.add("scale-125", "text-primary-600", "font-extrabold");
                    setTimeout(() => {
                        countEl.classList.remove("scale-125", "text-primary-600", "font-extrabold");
                    }, 500);
                }

                btn.classList.add("bg-primary-50", "text-primary-700", "border-primary-300", "dark:bg-primary-950", "dark:text-primary-300");
                const labelText = btn.querySelector(".upvote-label");
                if (labelText) labelText.textContent = "Confirmed ✓";

            } catch (err) {
                console.error("Upvote Error:", err);
                btn.innerHTML = originalHtml;
                btn.disabled = false;
            }
        });
    });
}
