// This file is part of the Django Quickstart project
// It contains the JavaScript code for the home page of the JSON app
// It uses the Fetch API to communicate with the Django backend and expects JSON responses

// The main functionalities include:
// - Fetching and displaying data for each table    
// - Opening modals for creating and editing entries
// - Submitting forms with validation and error handling
// - Handling file uploads with base64 encoding
// - Deleting entries with confirmation prompts
// - Rendering form fields dynamically based on the table structure
// - Formatting data for better readability in the UI
// - Managing relationships between tables (foreign keys, many-to-many, etc.)
// - Providing a user-friendly interface for CRUD operations
// - Ensuring compatibility with various field types (text, date, time, file, image, boolean, etc.)
// - Using CSRF tokens for secure form submissions
// - Handling errors gracefully and providing feedback to the user

let currentData = [];
let table2Options = [];
let table3Options = [];
let currentTable = null;
let paginationInfo = {enabled:false, page:1, page_size:5, total_pages:1, has_next:false, has_previous:false, total_items:0};

function loadStoredPageSize(table){
    const stored = localStorage.getItem('page_size_'+table);
    if(stored){
        const val = parseInt(stored);
        if(!isNaN(val)) paginationInfo.page_size = val;
    }
}

// This is used to render the correct table and form fields
function getCrudUrl(table) {
    return `/json_app/${table}/`;
}

// This function is called when the user clicks on a table link
function showTable(table, page=1) {
    document.getElementById('current_table').innerText = table.replace('table', 'Table ');
    currentTable = table;
    loadStoredPageSize(table);
    const params = new URLSearchParams({page: page, page_size: paginationInfo.page_size});
    fetch(getCrudUrl(table) + '?' + params.toString(), {method: 'GET'})
        .then(response => response.json())
        .then(data => {
            currentData = data.data || [];
            if (data.pagination) {
                if(data.pagination.enabled === false){
                    paginationInfo = {enabled:false,page:1,page_size:paginationInfo.page_size,total_pages:1,has_next:false,has_previous:false,total_items:data.pagination.total_items||0};
                } else {
                    paginationInfo = {enabled:true,...data.pagination};
                }
            } else {
                paginationInfo = {enabled:false,page:1,page_size:paginationInfo.page_size,total_pages:1,has_next:false,has_previous:false,total_items:0};
            }
            if (table === 'table1') {
                table2Options = data.table2_options || [];
                table3Options = data.table3_options || [];
            }
            renderTable();
        });
}

// This function renders the table based on the current data
function renderTable() {
    let info = document.querySelector(".info");
    if (info) {
        info.remove();
    }
    if (!currentData.length) {
        let html_no = `<span class="tablediv_title">${currentTable.replace('table', 'Table ')}</span>`;
        html_no += `<br>`;
        html_no += `<span class="tablediv_title">No entries found :( (It creates the modal based on the table)</span>`;
        document.getElementById('tableDiv').innerHTML = html_no;
        return;
    }
    let fields = Object.keys(currentData[0]);
    let html = `<span class="tablediv_title">${currentTable.replace('table', 'Table ')}</span>`;
    html += `<br>`;
    html += `<button class="tablediv_button" onclick="openCrudModal('create')">Add New Entry +</button>`;
    html += `<div class="table-container"><table class="crud-table"><thead><tr>`;
    fields.forEach(f => html += `<th>${formatHeader(f)}</th>`);
    html += `<th>Actions</th></tr></thead><tbody>`;
    currentData.forEach(row => {
        html += `<tr>`;
        fields.forEach(f => html += `<td>${formatCell(f, row[f])}</td>`);
        html += `<td>
            <button class="edit_button" onclick="openCrudModal('edit', ${row.id})"><i class="bi bi-pencil-square"></i> Edit</button>
            <button class="delete_button" onclick="deleteEntry(${row.id})"><i class="bi bi-trash-fill"></i> Delete</button>
        </td>`;
        html += `</tr>`;
    });
    html += `</tbody></table></div>`;
    html += renderPagination();
    document.getElementById('tableDiv').innerHTML = html;
}


function formatHeader(field) {
    // Capitalize and add spaces for better readability
    return field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// This function formats the cell values based on their type
function formatCell(field, value) {
    // Table1: image_field, file_field, boolean_field
    if (field === 'image_field') {
        if (value) {
            return `<img src="${value}" alt="img">`;
        } else {
            return '-';
        }
    }
    if (field === 'file_field') {
        if (value) {
            return `<a href="${value}" download>Download</a>`;
        } else {
            return '-';
        }
    }
    if (field === 'boolean_field') {
        return value ? 'True' : 'False';
    }
    
    // Table1: date_field, time_field, datetime_field, duration_field
    if (field === 'date_field' && value) {
        return new Date(value).toLocaleDateString();
    }
    if (field === 'time_field' && value) {
        return value;
    }
    if (field === 'datetime_field' && value) {
        return new Date(value).toLocaleString();
    }
    
    if (field === 'duration_field' && value) {
        const regex = /P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/;
        const match = value.match(regex);
        if (!match) return null;
        const days = parseInt(match[1] || 0);
        const hours = parseInt(match[2] || 0);
        const minutes = parseInt(match[3] || 0);
        const seconds = parseInt(match[4] || 0);
        return `${days} days, ${hours} hours, ${minutes} minutes, ${seconds} seconds`;
    }

    // Table1: foreign_key, one_to_one, many_to_many
    if ((field === 'foreign_key' || field === 'one_to_one') && value) {
        if (typeof value === 'object' && value.positive_small_int !== undefined) {
            return `Table2 id:${value.id} (${value.positive_small_int})`;
        }
        return '-';
    }
    
    if (field === 'many_to_many') {
        if (Array.isArray(value) && value.length) {
            return value.map(item => 
                typeof item === 'object' ? 
                `Table3 id:${item.id} (${item.email_field})` : 
                item
            ).join(', ');
        }
        return '-';
    }

    // Show empty as dash
    if (value === null || value === undefined || value === '') {
        return '-';
    }
    
    return value;
}

// This function opens the modal for creating or editing entries
function openCrudModal(mode, id=null) {
    document.getElementById('grey_background').style.display = 'block';
    document.getElementById('crudTable').value = currentTable;
    document.getElementById('crudId').value = id || '';
    document.getElementById('crudModal').style.display = 'block';
    document.getElementById('crudTitle').innerText = mode === 'create' ? 'Create Entry' : 'Edit Entry';
    document.getElementById('crudSubmitBtn').innerHTML = mode === 'create' ? '<i class="bi bi-save"></i> Create' : '<i class="bi bi-pencil"></i> Update';
    let data = {};
    // If editing, fetch the current data for the entry
    if (mode === 'edit' && id) {
        data = currentData.find(d => d.id == id) || {};
    }

    // If it's Table1, fetch the options for foreign keys and many-to-many fields
    if (currentTable === 'table1') {
        fetch(getCrudUrl('table1'), {method: 'GET'})
            .then(response => response.json())
            .then(resp => {
                table2Options = resp.table2_options || [];
                table3Options = resp.table3_options || [];
                renderFormFields(data);
            });
    } else {
        renderFormFields(data);
    }
}
// This function renders the form fields based on the current table and data
function renderFormFields(data = {}) {
    // Get the current fields based on the data
    const fields = currentData.length ? Object.keys(currentData[0]).filter(f => f !== 'id') : [];
    const formFields = [];

    fields.forEach(field => {
        // Render different field types based on the current table and field type
        if (currentTable === 'table1') {
            switch(field) {
                case 'foreign_key':
                case 'one_to_one':
                    formFields.push(renderSelect(field, table2Options, data[field]?.id));
                    break;
                
                case 'many_to_many':
                    formFields.push(renderMultiSelect(field, table3Options, (data[field] || []).map(item => item.id)));
                    break;
                
                case 'image_field':
                case 'file_field':
                    formFields.push(renderFileInput(field, data[field]));
                    break;
                
                case 'boolean_field':
                    formFields.push(renderCheckbox(field, data[field]));
                    break;
                
                case 'date_field':
                    formFields.push(renderDateInput(field, data[field]));
                    break;
                
                case 'time_field':
                    formFields.push(renderTimeInput(field, data[field]));
                    break;
                
                case 'datetime_field':
                    formFields.push(renderDateTimeInput(field, data[field]));
                    break;
                default:
                    formFields.push(renderTextInput(field, data[field]));
            }
        } else if (currentTable === 'table2') {
            // For Table2, render a select with two options for positive_small_int field
            if (field === 'positive_small_int') {
                const options = [
                    { id: 1, label: 'option1' },
                    { id: 2, label: 'option2' }
                ];
                formFields.push(`
                    <div class="form-row">
                        <label class="label_field">${formatHeader(field)}:</label>
                        <select class="input_field" name="${field}">
                            ${options.map(opt => `
                                <option value="${opt.id}" ${data[field] === opt.id ? 'selected' : ''}>
                                    ${opt.label}
                                </option>
                            `).join('')}
                        </select>
                    </div>`);
            } else {
                formFields.push(renderTextInput(field, data[field]));
            }
        } else {
            formFields.push(renderTextInput(field, data[field]));
        }
    });
    
    document.getElementById('formFields').innerHTML = formFields.join('');
}

// This function renders the form fields based on the field type
// It handles different input types like select, multi-select, file input, checkbox, date, time, datetime, duration, and text input
function renderSelect(field, options, selectedId) {
    return `
        <div class="form-row">
        <label class="label_field">${formatHeader(field)}:</label>
            <select class="input_field" name="${field}">
                <option value="">-- Select ${formatHeader(field)} --</option>
                ${options.map(opt => `
                    <option value="${opt.id}" ${selectedId === opt.id ? 'selected' : ''}>
                        ${opt.id} - Table2 (${opt.positive_small_int})
                    </option>
                `).join('')}
            </select>
        </div>`;
}

function renderMultiSelect(field, options, selectedIds) {
    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)}:</label>
            <select class="input_field" name="${field}" multiple size="3" style="height:auto;">
                ${options.map(opt => `
                    <option value="${opt.id}" ${selectedIds.includes(opt.id) ? 'selected' : ''}>
                        ${opt.id} - Table3 (${opt.email_field})
                    </option>
                `).join('')}
            </select>
        </div>`;
}

function renderFileInput(field, currentValue) {
    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)}:</label>
            ${currentValue ? `Current: ${currentValue}` : ''}
            <input class="input_field" type="file" name="${field}">
        </div>`;
}

function renderCheckbox(field, checked) {
    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)}:</label>
            <input style="height:20px" class="input_field" type="checkbox" name="${field}" ${checked ? 'checked' : ''}>
        </div>`;
}

function renderDateInput(field, value) {
    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)}:</label>
            <input class="input_field" type="date" name="${field}" value="${value ? value.split('T')[0] : ''}">
        </div>`;
}

function renderTimeInput(field, value) {
    return `
        <div class="form-row">
            <label class="label_field" >${formatHeader(field)}:</label>
            <input class="input_field" type="time" name="${field}" value="${value || ''}">
        </div>`;
}

function renderDateTimeInput(field, value) {
    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)}:</label>
            <input class="input_field" type="datetime-local" name="${field}" value="${value ? value.replace('Z', '') : ''}">
        </div>`;
}

function renderDurationInput(field, value) {
    let days = 0, hours = 0, minutes = 0;

    if (value) {
        let parts = value.trim().split(',');
        if (parts.length === 2) {
            days = parseInt(parts[0]);
            [hours, minutes] = parts[1].trim().split(':').map(Number);
        } else {
            [hours, minutes] = parts[0].split(':').map(Number);
        }
    }

    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)}:<br>
                Days: <input class="input_field" type="number" name="${field}_days" value="${days}" min="0" style="width: 60px;">
                Hours: <input class="input_field" type="number" name="${field}_hours" value="${hours}" min="0" max="23" style="width: 60px;">
                Minutes: <input class="input_field" type="number" name="${field}_minutes" value="${minutes}" min="0" max="59" style="width: 60px;">
            </label>
        </div>`;
}

function renderTextInput(field, value) {
    return `<div class="form-row"><label class="label_field">${formatHeader(field)}:</label> <input class="input_field" name="${field}" value="${value || ''}"></div>`;
}
    
// Submits the form data to the server
function submitCrud(e) {
    e.preventDefault();
    const form = document.getElementById('crudForm');
    const table = form.elements['crudTable'].value;
    const id = form.elements['crudId'].value;
    const method = id ? 'PUT' : 'POST';
    const url = getCrudUrl(table);

    // Check if we have files
    const hasFiles = (
        (form.elements['image_field']?.files?.length > 0) || 
        (form.elements['file_field']?.files?.length > 0)
    );

    // Prepare base data object
    const jsonData = prepareFormData(form);
    
    // Add the ID for PUT requests
    if (method === 'PUT') {
        jsonData.id = parseInt(id);
    }

    if (hasFiles) {
        // Handle files with base64
        handleFilesAndSubmit(form, jsonData, url, method);
    } else {
        // Direct JSON submission for no files
        submitJsonData(jsonData, url, method);
    }
}

// Prepares the form data for submission
function prepareFormData(form) {
    const jsonData = {};
    
    // Iterate through form elements to build the JSON object
    for (const field of form.elements) {
        if (!field.name || field.name === 'crudTable' || field.name === 'crudId') continue;
        if (field.name === 'many_to_many' && field.multiple) {
            jsonData[field.name] = Array.from(field.selectedOptions).map(opt => ({
                id: parseInt(opt.value)
            }));
        } else if (field.name === 'foreign_key' || field.name === 'one_to_one') {
            jsonData[field.name] = field.value ? { id: parseInt(field.value) } : null;
        } else if (field.type === 'checkbox') {
            jsonData[field.name] = field.checked;
        } else if (field.type !== 'file') {
            jsonData[field.name] = field.value || null;
        }
    }

    return jsonData;
}

// Handles file uploads and submits the form data
function handleFilesAndSubmit(form, jsonData, url, method) {
    const filePromises = [];
    const fileFields = ['image_field', 'file_field'];

    // Iterate through file fields to read files as base64
    fileFields.forEach(fieldName => {
        const fileInput = form.elements[fieldName];
        if (fileInput?.files?.length > 0) {
            const file = fileInput.files[0];
            // Create a promise to read the file as base64
            const promise = new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onloadend = () => {
                    resolve({
                        fieldName,
                        fileName: file.name,
                        content: reader.result
                    });
                };
                reader.onerror = reject;
                reader.readAsDataURL(file);
            });
            filePromises.push(promise);
        }
    });

    // Wait for all file reads to complete
    Promise.all(filePromises)
        .then(files => {
            // Add file data to the JSON object
            files.forEach(file => {
                jsonData[file.fieldName] = {
                    name: file.fileName,
                    content: file.content
                };
            });
            return submitJsonData(jsonData, url, method);
        })
        .catch(handleError);
}

// Submits the JSON data to the server
function submitJsonData(jsonData, url, method) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(jsonData)
    })
    // Handle the response and update the UI
    .then(handleResponse)
    .then(data => {
        showTable(document.getElementById('crudTable').value);
        closeCrud();
    })
    .catch(handleError);
}

// Handles the response from the server
function handleResponse(response) {
    if (!response.ok) {
        return response.text().then(text => {
            try {
                // Try to parse as JSON
                const json = JSON.parse(text);
                if (json.error) {
                    throw new Error(json.error);
                }
            } catch (e) {
                // Check for specific error types
                if (text.includes("UNIQUE constraint") || text.includes("duplicate key")) {
                    throw new Error("This email is already registered. Please use a different email address.");
                }
                // Check if response is HTML error page
                if (text.startsWith("<!DOCTYPE") || text.startsWith("<html")) {
                    throw new Error("Server error occurred. Please try again.");
                }
                throw new Error(text || `Error: ${response.status}`);
            }
        });
    }
    return response.json();
}

// Handles errors during the fetch operations
function handleError(error) {
    console.error('Error:', error);
    let errorMessage = error.message || 'An unknown error occurred';
    
    // Improve error messages to be more user-friendly
    if (errorMessage.includes("<!DOCTYPE") || errorMessage.includes("Unexpected token")) {
        errorMessage = "Server error occurred. Please try again.";
    } else if (errorMessage.includes("UNIQUE constraint") || errorMessage.includes("duplicate key")) {
        errorMessage = "This email is already registered. Please use a different email address.";
    } else if (errorMessage.includes("codec can't decode")) {
        errorMessage = "Error processing file upload. Please try again.";
    }

    // Create a div for displaying the error message
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 4px;
        border: 1px solid #f5c6cb;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        z-index: 1000;
        max-width: 300px;
    `;
    errorDiv.innerHTML = `<strong>Error:</strong> ${errorMessage}`;
    
    // Add the error div to the document
    document.body.appendChild(errorDiv);
    
    // Remove it after 5 seconds with a fade effect
    setTimeout(() => {
        errorDiv.style.opacity = '0';
        errorDiv.style.transition = 'opacity 0.5s';
        setTimeout(() => errorDiv.remove(), 500);
    }, 5000);
}

// Deletes an entry after user confirmation
function deleteEntry(id) {
    if (!confirm('Are you sure you want to delete this entry?')) return;
    let url = getCrudUrl(currentTable);
    fetch(url, {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({id: id})
    })
    .then(response => {
        showTable(currentTable);
    });
}

// Closes the CRUD modal and resets the form
function closeCrud() {
    document.getElementById('grey_background').style.display = 'none';
    document.getElementById('crudModal').style.display = 'none';
    document.getElementById('crudForm').reset();
}

// Utility function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function renderPagination() {
    if (!paginationInfo || paginationInfo.enabled === false) {
        return '';
    }
    const {page, total_pages, has_next, has_previous} = paginationInfo;
    let html = '<div class="pagination-controls" style="margin-top:10px;display:flex;align-items:center;gap:1px;">';
    html += `<span class="tablediv_title" style="margin-right:15px">Page ${page} of ${total_pages}</span> `;
    html += `<button ${has_previous? '' : 'disabled'} onclick="changePage(${page-1})" class="dark_button" style="margin-right:5px">< Prev</button>`;
    html += `<button ${has_next? '' : 'disabled'} onclick="changePage(${page+1})" class="dark_button" >Next ></button>`;
    html += `<hr class="vertical_line" style="margin:10px"><span class="tablediv_title" style="margin-right:5px">Page size:</span> <select onchange="changePageSize(this.value)" class="dark_button" style="padding:10px">`;
    [5,10,20,50,100].forEach(size => {
        html += `<option value="${size}" ${size==paginationInfo.page_size?'selected':''}>${size}</option>`;
    });
    html += '</select>';
    html += '</div>';
    return html;
}

function changePage(newPage) {
    if (newPage < 1 || newPage > paginationInfo.total_pages) return;
    showTable(currentTable, newPage);
}

function changePageSize(size) {
    const val = parseInt(size) || 10;
    paginationInfo.page_size = val;
    if(currentTable){
        localStorage.setItem('page_size_'+currentTable, val);
    }
    showTable(currentTable, 1);
}