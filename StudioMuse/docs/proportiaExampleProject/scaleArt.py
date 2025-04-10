import math
import json
import os
from flask import Flask, request, render_template_string, redirect, url_for, jsonify

app = Flask(__name__)

# File to store saved dimensions
DIMENSIONS_FILE = 'saved_dimensions.json'

# Load saved dimensions from file and ensure all values are floats
def load_dimensions():
    if os.path.exists(DIMENSIONS_FILE):
        try:
            with open(DIMENSIONS_FILE, 'r') as f:
                data = json.load(f)
                
                # Handle different formats
                if isinstance(data, dict):
                    # Convert old format to new format with default group
                    dimensions_list = []
                    for name, value in data.items():
                        try:
                            dimensions_list.append({
                                'name': name,
                                'value': float(value),
                                'group': 'Default'
                            })
                        except (ValueError, TypeError):
                            dimensions_list.append({
                                'name': name,
                                'value': 0.0,
                                'group': 'Default'
                            })
                    return dimensions_list
                else:
                    # Already in list format, ensure values are floats and add group if missing
                    for item in data:
                        try:
                            item['value'] = float(item['value'])
                        except (ValueError, TypeError):
                            item['value'] = 0.0
                        # Add group field if it doesn't exist
                        if 'group' not in item:
                            item['group'] = 'Default'
                    return data
        except json.JSONDecodeError:
            return []
    return []

# Save dimensions to file
def save_dimensions(dimensions_list):
    with open(DIMENSIONS_FILE, 'w') as f:
        json.dump(dimensions_list, f)

# Add a new dimension
def add_dimension(name, value, group='Default'):
    dimensions = load_dimensions()
    dimensions.append({
        'name': name,
        'value': round(float(value), 2),
        'group': group
    })
    save_dimensions(dimensions)

# Delete dimension from file
def delete_dimension(index):
    dimensions = load_dimensions()
    if 0 <= index < len(dimensions):
        dimensions.pop(index)
        save_dimensions(dimensions)

# Rename dimension
def rename_dimension(index, new_name):
    dimensions = load_dimensions()
    if 0 <= index < len(dimensions):
        dimensions[index]['name'] = new_name
        save_dimensions(dimensions)

# Reorder dimensions based on new order of indices
def reorder_dimensions(new_order):
    dimensions = load_dimensions()
    if len(new_order) != len(dimensions):
        return False
    
    # Create a new list with the reordered dimensions
    reordered = []
    for idx in new_order:
        if 0 <= idx < len(dimensions):
            reordered.append(dimensions[idx])
        else:
            return False
    
    save_dimensions(reordered)
    return True

# Update dimension group
def update_dimension_group(index, new_group):
    dimensions = load_dimensions()
    if 0 <= index < len(dimensions):
        dimensions[index]['group'] = new_group
        save_dimensions(dimensions)
        return True
    return False

# Get all unique groups
def get_groups():
    dimensions = load_dimensions()
    groups = set()
    for dim in dimensions:
        groups.add(dim.get('group', 'Default'))
    return sorted(list(groups))

# Reorder groups based on new order
def reorder_groups(new_order):
    dimensions = load_dimensions()
    if not dimensions:
        return False
    
    # Get all unique groups in their current order
    current_groups = []
    for dim in dimensions:
        group = dim.get('group', 'Default')
        if group not in current_groups:
            current_groups.append(group)
    
    # Validate the new order
    if len(new_order) != len(current_groups):
        return False
    
    for idx in new_order:
        if idx < 0 or idx >= len(current_groups):
            return False
    
    # Create a mapping of old group positions to new positions
    new_groups = []
    for idx in new_order:
        new_groups.append(current_groups[idx])
    
    # Create a new list with dimensions in the new group order
    reordered = []
    for group in new_groups:
        for dim in dimensions:
            if dim.get('group', 'Default') == group:
                reordered.append(dim)
    
    save_dimensions(reordered)
    return True

# HTML template with a simple form, result display, and saved dimensions sidebar
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Multiply by √2</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            display: flex;
        }
        .main-container {
            flex: 3;
            max-width: 500px;
            margin-right: 20px;
        }
        .sidebar {
            flex: 1;
            background-color: #f0f0f0;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            min-width: 250px;
        }
        .container {
            background-color: #f5f5f5;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .result {
            margin-top: 20px;
            padding: 10px;
            background-color: #e0f7fa;
            border-radius: 5px;
        }
        .save-form {
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        input[type="number"], input[type="text"] {
            padding: 8px;
            width: 100%;
            box-sizing: border-box;
            margin-bottom: 10px;
        }
        button {
            padding: 8px 15px;
            background-color: #4caf50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .dimensions-list {
            min-height: 50px;
        }
        .dimension-item {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 8px;
            background-color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: move;
            transition: background-color 0.2s, transform 0.1s;
        }
        .dimension-item:hover {
            background-color: #f9f9f9;
        }
        .dimension-item.dragging {
            opacity: 0.5;
            transform: scale(0.98);
        }
        .dimension-item.drag-over {
            border: 2px dashed #4caf50;
            padding: 7px;
        }
        .dimension-content {
            flex-grow: 1;
        }
        .dimension-actions {
            display: flex;
            align-items: center;
        }
        .dimension-drag-handle {
            cursor: move;
            color: #999;
            margin-right: 10px;
            font-size: 16px;
        }
        h2 {
            margin-top: 0;
            color: #333;
        }
        .action-btn {
            color: #999;
            cursor: pointer;
            font-weight: normal;
            margin-left: 10px;
            text-decoration: none;
            font-size: 16px;
        }
        .action-btn:hover {
            color: #333;
            font-weight: bold;
        }
        .delete-btn:hover {
            color: #ff0000;
        }
        .edit-btn:hover {
            color: #2196F3;
        }
        .edit-form {
            display: none;
            margin-top: 8px;
            padding: 8px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }
        .edit-form input {
            margin-bottom: 8px;
        }
        .edit-form-buttons {
            display: flex;
            justify-content: space-between;
        }
        .edit-form-buttons button {
            flex: 1;
            margin-right: 4px;
        }
        .edit-form-buttons button:last-child {
            margin-right: 0;
        }
        .status-message {
            margin-top: 10px;
            padding: 8px;
            border-radius: 4px;
            display: none;
        }
        .status-success {
            background-color: #e8f5e9;
            color: #2e7d32;
        }
        .status-error {
            background-color: #ffebee;
            color: #c62828;
        }
        /* Group styles */
        .group-container {
            margin-bottom: 15px;
        }
        
        .group-header {
            background-color: #e0e0e0;
            padding: 8px 12px;
            margin-top: 15px;
            margin-bottom: 8px;
            border-radius: 4px;
            font-weight: bold;
            cursor: move;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .group-header:hover {
            background-color: #d0d0d0;
        }
        
        .group-header.dragging {
            opacity: 0.5;
            transform: scale(0.98);
        }
        
        .group-header.drag-over {
            border: 2px dashed #4caf50;
            padding: 6px 10px;
        }
        
        .group-toggle-btn {
            cursor: pointer;
            margin-left: 10px;
        }
        
        .group-drag-handle {
            cursor: move;
            color: #999;
            margin-right: 10px;
            font-size: 16px;
        }
        
        .group-content {
            margin-left: 10px;
        }
        
        .add-group-form {
            margin-top: 15px;
            padding: 10px;
            background-color: #f0f0f0;
            border-radius: 4px;
        }
        
        .group-selector {
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
        }
        
        .collapsed {
            display: none;
        }
        
        .group-toggle {
            font-size: 18px;
        }
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const dimensionsList = document.getElementById('dimensions-list');
            let draggedItem = null;
            let dimensions = [];
            let groups = [];
            
            // Initialize the dimensions array with current indices
            document.querySelectorAll('.dimension-item').forEach((item, index) => {
                dimensions.push(index);
            });
            
            // Initialize the groups array with current indices
            document.querySelectorAll('.group-container').forEach((item, index) => {
                groups.push(index);
            });
            
            // Add event listeners for dimension drag and drop
            document.querySelectorAll('.dimension-item').forEach(item => {
                item.setAttribute('draggable', true);
                
                item.addEventListener('dragstart', function(e) {
                    draggedItem = this;
                    setTimeout(() => {
                        this.classList.add('dragging');
                    }, 0);
                    
                    // Store the original index
                    e.dataTransfer.setData('text/plain', this.getAttribute('data-index'));
                    e.dataTransfer.setData('type', 'dimension');
                });
                
                item.addEventListener('dragend', function() {
                    this.classList.remove('dragging');
                    document.querySelectorAll('.dimension-item').forEach(item => {
                        item.classList.remove('drag-over');
                    });
                });
                
                item.addEventListener('dragover', function(e) {
                    e.preventDefault();
                });
                
                item.addEventListener('dragenter', function(e) {
                    e.preventDefault();
                    if (this !== draggedItem && e.dataTransfer.getData('type') === 'dimension') {
                        this.classList.add('drag-over');
                    }
                });
                
                item.addEventListener('dragleave', function() {
                    this.classList.remove('drag-over');
                });
                
                item.addEventListener('drop', function(e) {
                    e.preventDefault();
                    this.classList.remove('drag-over');
                    
                    if (this !== draggedItem && e.dataTransfer.getData('type') === 'dimension') {
                        const fromIndex = parseInt(e.dataTransfer.getData('text/plain'));
                        const toIndex = parseInt(this.getAttribute('data-index'));
                        
                        // Reorder the dimensions array
                        const movedItem = dimensions.splice(fromIndex, 1)[0];
                        dimensions.splice(toIndex, 0, movedItem);
                        
                        // Send the new order to the server
                        saveNewOrder(dimensions);
                    }
                });
            });
            
            // Add event listeners for group drag and drop
            document.querySelectorAll('.group-header').forEach(item => {
                item.setAttribute('draggable', true);
                
                item.addEventListener('dragstart', function(e) {
                    draggedItem = this.parentNode; // The group container
                    setTimeout(() => {
                        this.classList.add('dragging');
                    }, 0);
                    
                    // Store the original index
                    e.dataTransfer.setData('text/plain', this.parentNode.getAttribute('data-index'));
                    e.dataTransfer.setData('type', 'group');
                });
                
                item.addEventListener('dragend', function() {
                    this.classList.remove('dragging');
                    document.querySelectorAll('.group-header').forEach(item => {
                        item.classList.remove('drag-over');
                    });
                });
                
                item.addEventListener('dragover', function(e) {
                    e.preventDefault();
                });
                
                item.addEventListener('dragenter', function(e) {
                    e.preventDefault();
                    if (this.parentNode !== draggedItem && e.dataTransfer.getData('type') === 'group') {
                        this.classList.add('drag-over');
                    }
                });
                
                item.addEventListener('dragleave', function() {
                    this.classList.remove('drag-over');
                });
                
                item.addEventListener('drop', function(e) {
                    e.preventDefault();
                    this.classList.remove('drag-over');
                    
                    if (this.parentNode !== draggedItem && e.dataTransfer.getData('type') === 'group') {
                        const fromIndex = parseInt(e.dataTransfer.getData('text/plain'));
                        const toIndex = parseInt(this.parentNode.getAttribute('data-index'));
                        
                        // Reorder the groups array
                        const movedItem = groups.splice(fromIndex, 1)[0];
                        groups.splice(toIndex, 0, movedItem);
                        
                        // Send the new order to the server
                        saveNewGroupOrder(groups);
                    }
                });
            });
            
            function saveNewOrder(newOrder) {
                fetch('/reorder', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ order: newOrder }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showStatus('Order updated successfully!', 'success');
                        // Reload the page to reflect the new order
                        setTimeout(() => {
                            window.location.reload();
                        }, 500);
                    } else {
                        showStatus('Failed to update order.', 'error');
                    }
                })
                .catch(error => {
                    showStatus('An error occurred.', 'error');
                    console.error('Error:', error);
                });
            }
            
            function saveNewGroupOrder(newOrder) {
                fetch('/reorder_groups', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ order: newOrder }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showStatus('Group order updated successfully!', 'success');
                        // Reload the page to reflect the new order
                        setTimeout(() => {
                            window.location.reload();
                        }, 500);
                    } else {
                        showStatus('Failed to update group order.', 'error');
                    }
                })
                .catch(error => {
                    showStatus('An error occurred.', 'error');
                    console.error('Error:', error);
                });
            }
            
            function showStatus(message, type) {
                const statusEl = document.getElementById('status-message');
                statusEl.textContent = message;
                statusEl.className = 'status-message';
                statusEl.classList.add('status-' + type);
                statusEl.style.display = 'block';
                
                setTimeout(() => {
                    statusEl.style.display = 'none';
                }, 3000);
            }
            
            // Toggle edit form
            window.toggleEditForm = function(index) {
                const form = document.getElementById(`edit-form-${index}`);
                form.style.display = form.style.display === 'none' ? 'block' : 'none';
            };
            
            // Toggle group
            window.toggleGroup = function(groupName, event) {
                // Prevent the click from triggering drag events
                if (event) {
                    event.stopPropagation();
                }
                
                const content = document.getElementById(`group-content-${groupName}`);
                const toggle = document.getElementById(`group-toggle-${groupName}`);
                
                // Get current URL and parameters
                let url = new URL(window.location.href);
                let params = new URLSearchParams(url.search);
                
                if (content.classList.contains('collapsed')) {
                    content.classList.remove('collapsed');
                    toggle.textContent = '−';
                    
                    // Add this group to open groups
                    params.append('open', groupName);
                } else {
                    content.classList.add('collapsed');
                    toggle.textContent = '+';
                    
                    // Remove this group from open groups
                    let openGroups = params.getAll('open');
                    params.delete('open');
                    for (let group of openGroups) {
                        if (group !== groupName) {
                            params.append('open', group);
                        }
                    }
                }
                
                // Update URL without reloading the page
                url.search = params.toString();
                window.history.pushState({}, '', url);
            };
            
            // Toggle group form
            window.toggleGroupForm = function(index) {
                const form = document.getElementById(`group-form-${index}`);
                form.style.display = form.style.display === 'none' ? 'block' : 'none';
            };
        });
    </script>
</head>
<body>
    <div class="main-container">
        <div class="container">
            <h1>Multiply by √2</h1>
            <form method="POST" action="/">
                <label for="number">Enter a number:</label>
                <input type="number" id="number" name="number" step="any" required value="{{ number if number else '' }}">
                <button type="submit">Calculate</button>
            </form>
            
            {% if result %}
            <div class="result">
                <p>{{ number }} × √2 = {{ "%.2f"|format(result) }}</p>
                <p>√2 ≈ {{ "%.2f"|format(sqrt2) }}</p>
                
                <div class="save-form">
                    <h3>Save this dimension</h3>
                    <form method="POST" action="/save">
                        <input type="hidden" name="value" value="{{ result }}">
                        <label for="dimension_name">Dimension name:</label>
                        <input type="text" id="dimension_name" name="dimension_name" required placeholder="e.g., Head Height">
                        
                        <label for="group">Group:</label>
                        <select name="group" id="group" class="group-selector">
                            {% for group in groups %}
                                <option value="{{ group }}">{{ group }}</option>
                            {% endfor %}
                            <option value="new">+ New Group</option>
                        </select>
                        
                        <div id="new-group-input" style="display: none;">
                            <label for="new_group">New Group Name:</label>
                            <input type="text" id="new_group" name="new_group" placeholder="Enter new group name">
                        </div>
                        
                        {% for group_id in open_groups %}
                            <input type="hidden" name="open_groups" value="{{ group_id }}">
                        {% endfor %}
                        
                        <button type="submit">Save</button>
                    </form>
                    
                    <script>
                        document.getElementById('group').addEventListener('change', function() {
                            const newGroupInput = document.getElementById('new-group-input');
                            if (this.value === 'new') {
                                newGroupInput.style.display = 'block';
                            } else {
                                newGroupInput.style.display = 'none';
                            }
                        });
                    </script>
                </div>
            </div>
            {% endif %}
        </div>
    </div>
    
    <div class="sidebar">
        <h2>Saved Dimensions</h2>
        <div id="status-message" class="status-message"></div>
        
        <div class="add-group-form">
            <form method="POST" action="/add_group">
                <label for="group_name">Add New Group:</label>
                <input type="text" id="group_name" name="group_name" required placeholder="Group name">
                <button type="submit">Add Group</button>
            </form>
        </div>
        
        <div id="dimensions-list" class="dimensions-list">
            {% if dimensions %}
                {% set grouped_dimensions = {} %}
                {% for dimension in dimensions %}
                    {% set group = dimension.get('group', 'Default') %}
                    {% if group not in grouped_dimensions %}
                        {% set _ = grouped_dimensions.update({group: []}) %}
                    {% endif %}
                    {% set _ = grouped_dimensions[group].append(dimension) %}
                {% endfor %}
                
                {% for group, items in grouped_dimensions.items() %}
                    {% set safe_group_id = group|replace(' ', '-')|replace('/', '')|replace('.', '')|lower %}
                    <div class="group-container" id="group-container-{{ loop.index0 }}" data-index="{{ loop.index0 }}">
                        <div class="group-header" id="group-header-{{ safe_group_id }}">
                            <div class="group-drag-handle">⋮⋮</div>
                            <span>{{ group }}</span>
                            <span id="group-toggle-{{ safe_group_id }}" class="group-toggle group-toggle-btn" onclick="toggleGroup('{{ safe_group_id }}', event)">{% if safe_group_id not in open_groups %}+{% else %}−{% endif %}</span>
                        </div>
                        <div id="group-content-{{ safe_group_id }}" class="group-content {% if safe_group_id not in open_groups %}collapsed{% endif %}">
                            {% for dimension in items %}
                                {% set index = dimensions.index(dimension) %}
                                <div class="dimension-item" id="dimension-{{ index }}" data-index="{{ index }}">
                                    <div class="dimension-drag-handle">⋮⋮</div>
                                    <div class="dimension-content">
                                        <strong>{{ dimension.name }}:</strong> {{ "%.2f"|format(dimension.value) }} centimeters
                                    </div>
                                    <div class="dimension-actions">
                                        <a href="#" class="action-btn edit-btn" title="Edit this dimension" onclick="toggleEditForm({{ index }}); return false;">✎</a>
                                        <a href="#" class="action-btn" title="Change group" onclick="toggleGroupForm({{ index }}); return false;">🏷️</a>
                                        <a href="/delete/{{ index }}" class="action-btn delete-btn" title="Delete this dimension">×</a>
                                    </div>
                                    
                                    <div id="edit-form-{{ index }}" class="edit-form">
                                        <form method="POST" action="/rename/{{ index }}">
                                            <label for="new_name_{{ index }}">Rename:</label>
                                            <input type="text" id="new_name_{{ index }}" name="new_name" value="{{ dimension.name }}" required>
                                            <div class="edit-form-buttons">
                                                <button type="submit">Save</button>
                                                <button type="button" onclick="toggleEditForm({{ index }})">Cancel</button>
                                            </div>
                                            {% for group_id in open_groups %}
                                                <input type="hidden" name="open_groups" value="{{ group_id }}">
                                            {% endfor %}
                                        </form>
                                    </div>
                                    
                                    <div id="group-form-{{ index }}" class="edit-form">
                                        <form method="POST" action="/update_group/{{ index }}">
                                            <label for="group_{{ index }}">Change Group:</label>
                                            <select name="group" id="group_{{ index }}" class="group-selector">
                                                {% for g in groups %}
                                                    <option value="{{ g }}" {% if g == dimension.get('group', 'Default') %}selected{% endif %}>{{ g }}</option>
                                                {% endfor %}
                                                <option value="new">+ New Group</option>
                                            </select>
                                            
                                            <div id="new-group-input-{{ index }}" style="display: none;">
                                                <label for="new_group_{{ index }}">New Group Name:</label>
                                                <input type="text" id="new_group_{{ index }}" name="new_group" placeholder="Enter new group name">
                                            </div>
                                            
                                            <div class="edit-form-buttons">
                                                <button type="submit">Save</button>
                                                <button type="button" onclick="toggleGroupForm({{ index }})">Cancel</button>
                                            </div>
                                            {% for group_id in open_groups %}
                                                <input type="hidden" name="open_groups" value="{{ group_id }}">
                                            {% endfor %}
                                        </form>
                                        
                                        <script>
                                            document.getElementById('group_{{ index }}').addEventListener('change', function() {
                                                const newGroupInput = document.getElementById('new-group-input-{{ index }}');
                                                if (this.value === 'new') {
                                                    newGroupInput.style.display = 'block';
                                                } else {
                                                    newGroupInput.style.display = 'none';
                                                }
                                            });
                                        </script>
                                    </div>
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                {% endfor %}
            {% else %}
                <p>No dimensions saved yet.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    number = None
    sqrt2 = math.sqrt(2)
    dimensions = load_dimensions()
    groups = get_groups()
    
    # Get open groups from URL parameters
    open_groups = request.args.getlist('open')
    
    if request.method == 'POST':
        try:
            number = float(request.form['number'])
            result = number * sqrt2
        except ValueError:
            pass
    
    return render_template_string(HTML_TEMPLATE, 
                                 result=result, 
                                 number=number, 
                                 sqrt2=sqrt2,
                                 dimensions=dimensions,
                                 groups=groups,
                                 open_groups=open_groups)

@app.route('/save', methods=['POST'])
def save():
    dimension_name = request.form.get('dimension_name')
    value = request.form.get('value')
    group = request.form.get('group', 'Default')
    
    # Preserve open groups
    open_groups = request.form.getlist('open_groups')
    
    # Handle new group creation
    if group == 'new':
        new_group = request.form.get('new_group')
        if new_group and new_group.strip():
            group = new_group.strip()
            # Automatically open the new group
            open_groups.append(group.replace(' ', '-').replace('/', '').replace('.', '').lower())
        else:
            group = 'Default'
    
    if dimension_name and value:
        add_dimension(dimension_name, value, group)
    
    redirect_url = url_for('index')
    if open_groups:
        redirect_url += '?' + '&'.join([f'open={group}' for group in open_groups])
    
    return redirect(redirect_url)

@app.route('/delete/<int:index>')
def delete(index):
    # Get the group before deleting the dimension
    dimensions = load_dimensions()
    group = None
    if 0 <= index < len(dimensions):
        group = dimensions[index].get('group', 'Default')
    
    delete_dimension(index)
    
    # Preserve open groups
    open_groups = request.args.getlist('open')
    if group:
        safe_group_id = group.replace(' ', '-').replace('/', '').replace('.', '').lower()
        if safe_group_id not in open_groups:
            open_groups.append(safe_group_id)
    
    redirect_url = url_for('index')
    if open_groups:
        redirect_url += '?' + '&'.join([f'open={group}' for group in open_groups])
    
    return redirect(redirect_url)

@app.route('/rename/<int:index>', methods=['POST'])
def rename(index):
    new_name = request.form.get('new_name')
    # Preserve open groups
    open_groups = request.form.getlist('open_groups')
    
    if new_name:
        rename_dimension(index, new_name)
    
    redirect_url = url_for('index')
    if open_groups:
        redirect_url += '?' + '&'.join([f'open={group}' for group in open_groups])
    
    return redirect(redirect_url)

@app.route('/reorder', methods=['POST'])
def reorder():
    data = request.json
    if data and 'order' in data:
        success = reorder_dimensions(data['order'])
        return jsonify({'success': success})
    return jsonify({'success': False})

@app.route('/update_group/<int:index>', methods=['POST'])
def update_group(index):
    group = request.form.get('group', 'Default')
    
    # Preserve open groups
    open_groups = request.form.getlist('open_groups')
    
    # Handle new group creation
    if group == 'new':
        new_group = request.form.get('new_group')
        if new_group and new_group.strip():
            group = new_group.strip()
            # Automatically open the new group
            safe_group_id = group.replace(' ', '-').replace('/', '').replace('.', '').lower()
            if safe_group_id not in open_groups:
                open_groups.append(safe_group_id)
        else:
            group = 'Default'
    
    if group:
        update_dimension_group(index, group)
    
    redirect_url = url_for('index')
    if open_groups:
        redirect_url += '?' + '&'.join([f'open={group}' for group in open_groups])
    
    return redirect(redirect_url)

@app.route('/add_group', methods=['POST'])
def add_group():
    group_name = request.form.get('group_name')
    
    # Preserve open groups
    open_groups = request.form.getlist('open_groups')
    
    # Add the new group to open groups
    if group_name:
        safe_group_id = group_name.replace(' ', '-').replace('/', '').replace('.', '').lower()
        if safe_group_id not in open_groups:
            open_groups.append(safe_group_id)
    
    redirect_url = url_for('index')
    if open_groups:
        redirect_url += '?' + '&'.join([f'open={group}' for group in open_groups])
    
    return redirect(redirect_url)

@app.route('/reorder_groups', methods=['POST'])
def reorder_groups_route():
    data = request.json
    if data and 'order' in data:
        success = reorder_groups(data['order'])
        return jsonify({'success': success})
    return jsonify({'success': False})

if __name__ == '__main__':
    print("Server starting at http://127.0.0.1:5000/")
    app.run(debug=True)
