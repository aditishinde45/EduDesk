/* =============================================================================
   EduDesk - Client Scripts
   Interactive UI enhancements, dynamic inputs, and department-course filtering
============================================================================= */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Sidebar Toggle on Mobile
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function (e) {
            e.preventDefault();
            document.getElementById('sidebar-wrapper').classList.toggle('toggled');
        });
    }

    // 2. Dynamic Phone Numbers (Student and Authority forms)
    const addPhoneBtn = document.getElementById('addPhoneBtn');
    const phoneContainer = document.getElementById('phoneContainer');

    if (addPhoneBtn && phoneContainer) {
        addPhoneBtn.addEventListener('click', function () {
            const row = document.createElement('div');
            row.className = 'phone-input-row d-flex gap-2 mb-2';
            row.innerHTML = `
                <input type="text" name="phones[]" class="form-control" placeholder="e.g. 9876543210" pattern="^\\+?[0-9]{10,15}$" title="Phone number must be 10 to 15 digits" required>
                <button type="button" class="btn btn-outline-danger btn-sm remove-phone-btn" title="Remove phone">
                    <i class="bi bi-trash"></i>
                </button>
            `;
            phoneContainer.appendChild(row);
        });

        phoneContainer.addEventListener('click', function (e) {
            if (e.target.closest('.remove-phone-btn')) {
                const row = e.target.closest('.phone-input-row');
                // Ensure at least one input field remains if required
                if (phoneContainer.querySelectorAll('.phone-input-row').length > 1) {
                    row.remove();
                } else {
                    row.querySelector('input').value = '';
                }
            }
        });
    }

    // 3. Dynamic Course Dropdown Filter based on selected Department
    const deptSelect = document.getElementById('department_id');
    const courseSelect = document.getElementById('course_id');

    if (deptSelect && courseSelect) {
        deptSelect.addEventListener('change', function () {
            const deptId = this.value;
            if (!deptId) {
                courseSelect.innerHTML = '<option value="">-- First Select Department --</option>';
                return;
            }

            courseSelect.innerHTML = '<option value="">Loading courses...</option>';
            fetch(`/courses/by-department/${deptId}`)
                .then(response => response.json())
                .then(data => {
                    let options = '<option value="">-- Select Course --</option>';
                    data.forEach(course => {
                        const durationText = course.duration ? ` (${course.duration})` : '';
                        options += `<option value="${course.id}">${course.name}${durationText}</option>`;
                    });
                    courseSelect.innerHTML = options;
                })
                .catch(err => {
                    console.error('Error fetching courses:', err);
                    courseSelect.innerHTML = '<option value="">Error loading courses</option>';
                });
        });
    }

    // 4. Client-side Derived Age Calculator on Student form
    const dobInput = document.getElementById('dob');
    const ageBadge = document.getElementById('computed_age_badge');

    if (dobInput && ageBadge) {
        function updateAge() {
            if (!dobInput.value) {
                ageBadge.textContent = 'Derived Age: --';
                return;
            }
            const birthDate = new Date(dobInput.value);
            const today = new Date();
            let age = today.getFullYear() - birthDate.getFullYear();
            const m = today.getMonth() - birthDate.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }
            if (age >= 0 && age < 120) {
                ageBadge.textContent = `Derived Age: ${age} years`;
            } else {
                ageBadge.textContent = 'Derived Age: Invalid Date';
            }
        }
        dobInput.addEventListener('change', updateAge);
        updateAge();
    }

    // 5. Delete Confirmation Modal Hook
    const deleteModal = document.getElementById('deleteConfirmModal');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const actionUrl = button.getAttribute('data-action');
            const itemName = button.getAttribute('data-item-name') || 'this item';
            
            const form = deleteModal.querySelector('#deleteForm');
            const itemSpan = deleteModal.querySelector('#deleteItemName');
            
            if (form) form.action = actionUrl;
            if (itemSpan) itemSpan.textContent = itemName;
        });
    }

    // 6. Revocation Modal Hook
    const revokeModal = document.getElementById('revokeModal');
    if (revokeModal) {
        revokeModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const actionUrl = button.getAttribute('data-action');
            const certNo = button.getAttribute('data-cert-no');
            
            const form = revokeModal.querySelector('#revokeForm');
            const certNoSpan = revokeModal.querySelector('#revokeCertNo');
            
            if (form) form.action = actionUrl;
            if (certNoSpan) certNoSpan.textContent = certNo;
        });
    }

    // 7. Auto-dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 6000);
    });
});
