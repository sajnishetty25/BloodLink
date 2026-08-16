// UI Functions
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    sidebar.classList.toggle('active');
    content.classList.toggle('shifted');
}

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });
    document.getElementById(sectionId).classList.remove('hidden');
}

// Appointment Booking Functions
function setupAppointmentForm() {
    const appointmentForm = document.getElementById("appointmentForm");
    if (!appointmentForm) return;

    appointmentForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const city = document.getElementById("city").value.trim();
        const medicalHistory = document.getElementById("medical_history").value.trim();

        if (!city) {
            alert("Please select a city");
            return;
        }

        try {
            const response = await fetch("/book_appointment", {
                method: "POST",
                body: JSON.stringify({ 
                    city: city, 
                    medical_history: medicalHistory 
                }),
                headers: { "Content-Type": "application/json" }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log("Blood banks received:", data);

            const bloodBankSelect = document.getElementById("bloodbank");
            bloodBankSelect.innerHTML = "";

            if (!data || data.length === 0) {
                alert("No blood banks found in this city!");
                return;
            }

            data.forEach(bank => {
                const option = document.createElement("option");
                option.value = bank.bloodbank_id;
                option.textContent = `${bank.name} - ${bank.city}`;
                bloodBankSelect.appendChild(option);
            });

            document.getElementById("bloodbanks_section").classList.remove("hidden");
        } catch (error) {
            console.error("Error fetching blood banks:", error);
            alert("Failed to fetch blood banks. Please try again.");
        }
    });
}

function setupTimeslotForm() {
    const timeslotForm = document.getElementById("select_timeslot_form");
    if (!timeslotForm) return;

    timeslotForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const bloodbankId = document.getElementById("bloodbank").value;

        if (!bloodbankId) {
            alert("Please select a blood bank first");
            return;
        }

        try {
            const response = await fetch("/select_timeslot", {
                method: "POST",
                body: JSON.stringify({ bloodbank: bloodbankId }),
                headers: { "Content-Type": "application/json" }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log("Time slots received:", data);

            const timeSlotSelect = document.getElementById("timeslot");
            timeSlotSelect.innerHTML = "";

            if (!data || data.length === 0) {
                alert("No available time slots found!");
                return;
            }

            data.forEach(slot => {
                const option = document.createElement("option");
                option.value = slot.id;
                option.textContent = slot.slot;
                timeSlotSelect.appendChild(option);
            });

            document.getElementById("timeslots_section").classList.remove("hidden");
        } catch (error) {
            console.error("Error fetching time slots:", error);
            alert("Failed to fetch time slots. Please try again.");
        }
    });
}

function setupDateValidation() {
    const dateInput = document.getElementById("appointment_date");
    const dateError = document.getElementById("date_error");
    const confirmForm = document.getElementById("confirm_appointment_form");

    if (!dateInput || !confirmForm) return;

    function setDateLimits() {
        const today = new Date();
        const maxDate = new Date();
        maxDate.setDate(today.getDate() + 10);

        const todayStr = today.toISOString().split("T")[0];
        const maxDateStr = maxDate.toISOString().split("T")[0];

        dateInput.min = todayStr;
        dateInput.max = maxDateStr;
    }

    setDateLimits();

    confirmForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const selectedDate = dateInput.value;
        const today = new Date().toISOString().split("T")[0];
        const maxDate = new Date();
        maxDate.setDate(new Date().getDate() + 10);
        const maxDateStr = maxDate.toISOString().split("T")[0];

        if (!selectedDate || selectedDate < today || selectedDate > maxDateStr) {
            dateError.style.display = "block";
            return;
        } else {
            dateError.style.display = "none";
        }

        const donorId = "{{ session['user_id'] }}";
        const bloodBankId = document.getElementById("bloodbank").value;
        const timeslotElement = document.getElementById("timeslot");
        const timeslotText = timeslotElement.options[timeslotElement.selectedIndex].text;
        const medicalHistory = document.getElementById("medical_history").value.trim();

        if (!bloodBankId || !timeslotText) {
            alert("Please complete all steps before confirming");
            return;
        }

        try {
            const response = await fetch("/confirm_appointment", {
                method: "POST",
                body: JSON.stringify({
                    donor_id: donorId,
                    blood_bank_id: bloodBankId,
                    appointment_date: selectedDate,
                    timeslot: timeslotText,
                    medical_history: medicalHistory
                }),
                headers: { "Content-Type": "application/json" }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Failed to book appointment");
            }

            if (data.success) {
                alert("✅ Appointment booked successfully!");
                loadBookedAppointments();
                document.getElementById("appointmentForm").reset();
                document.getElementById("bloodbanks_section").classList.add("hidden");
                document.getElementById("timeslots_section").classList.add("hidden");
            } else {
                alert("❌ " + (data.error || "Failed to book appointment"));
            }
        } catch (error) {
            console.error("Error booking appointment:", error);
            alert("Error booking appointment: " + error.message);
        }
    });
}

// Data Loading Functions
async function loadBookedAppointments() {
    try {
        const response = await fetch("/get_booked_appointments");
        const data = await response.json();

        const tableBody = document.getElementById("appointments_table_body");
        if (!tableBody) return;

        tableBody.innerHTML = "";

        if (!data || data.length === 0) {
            tableBody.innerHTML = "<tr><td colspan='6'>No appointments found.</td></tr>";
            return;
        }

        data.forEach(appointment => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${appointment.appointment_date || 'N/A'}</td>
                <td>${appointment.timeslot || 'N/A'}</td>
                <td>${appointment.blood_bank || 'N/A'}</td>
                <td>${appointment.city || 'N/A'}</td>
                <td>${appointment.status || 'N/A'}</td>
                <td>
                    ${appointment.receipt_generated ? 
                        `<button onclick="downloadReceipt(${appointment.appointment_id})" class="download-btn">Download Receipt</button>` : 
                        'Receipt not available'}
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error("Error loading booked appointments:", error);
        const tableBody = document.getElementById("appointments_table_body");
        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="6">Error loading appointments</td></tr>`;
        }
    }
}

function downloadReceipt(appointmentId) {
    window.open(`/download_receipt/${appointmentId}`, '_blank');
}

async function loadDonationHistory() {
    try {
        const response = await fetch("/get_donation_history");
        const data = await response.json();

        const historyTable = document.getElementById("donation_history_body");
        if (!historyTable) return;

        historyTable.innerHTML = "";

        if (data.error) {
            historyTable.innerHTML = `<tr><td colspan="4" style="color:red;">${data.error}</td></tr>`;
            return;
        }

        if (!data || data.length === 0) {
            historyTable.innerHTML = `<tr><td colspan="4">No donation history found.</td></tr>`;
            return;
        }

        data.forEach(entry => {
            historyTable.innerHTML += `
                <tr>
                    <td>${entry.date || 'N/A'}</td>
                    <td>${entry.blood_bank || 'N/A'}</td>
                    <td>${entry.city || 'N/A'}</td>
                    <td>${entry.blood_group || 'N/A'}</td>
                </tr>
            `;
        });
    } catch (error) {
        console.error("Error fetching donation history:", error);
        const historyTable = document.getElementById("donation_history_body");
        if (historyTable) {
            historyTable.innerHTML = `<tr><td colspan="4">Error loading donation history</td></tr>`;
        }
    }
}

async function updateDonationDates() {
    try {
        // Get DOM elements
        const lastDonationEl = document.getElementById("last_donation_date");
        const nextEligibleEl = document.getElementById("next_eligible_date");
        const errorEl = document.getElementById("date_error_message");

        // Show loading state
        if (lastDonationEl) lastDonationEl.textContent = "Loading...";
        if (nextEligibleEl) nextEligibleEl.textContent = "Loading...";
        if (errorEl) errorEl.textContent = "";

        // Fetch data
        const response = await fetch("/get_donation_dates");
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Format dates
        const formatDate = (dateString) => {
            if (!dateString) return null;
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
        };

        // Update DOM
        if (lastDonationEl) {
            lastDonationEl.textContent = formatDate(data.last_donation) || 'Never donated';
        }
        if (nextEligibleEl) {
            nextEligibleEl.textContent = formatDate(data.next_eligible) || 'Available now';
        }

    } catch (error) {
        console.error("Error updating donation dates:", error);
        
        // Update error message in UI
        const errorEl = document.getElementById("date_error_message");
        if (errorEl) {
            errorEl.textContent = "Failed to load donation dates. Please try again later.";
            errorEl.style.color = "red";
        }

        // Show fallback values
        const lastDonationEl = document.getElementById("last_donation_date");
        const nextEligibleEl = document.getElementById("next_eligible_date");
        if (lastDonationEl) lastDonationEl.textContent = "Error loading";
        if (nextEligibleEl) nextEligibleEl.textContent = "Error loading";
    }
}


// Initialization
function initializePage() {
    setupAppointmentForm();
    setupTimeslotForm();
    setupDateValidation();
    loadDonationHistory();
    loadBookedAppointments();
    updateDonationDates();
}

// Start the application when DOM is loaded
document.addEventListener("DOMContentLoaded", initializePage);