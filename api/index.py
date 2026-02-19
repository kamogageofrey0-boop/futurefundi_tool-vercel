from flask import Flask, render_template, request, redirect, url_for, session
import math

app = Flask(__name__)
app.secret_key = 'futurefundi-secret-2024'

# -------------------
# Data and defaults
# -------------------
PATHWAY_DATA = {
    'Robotics': {
        'resources': ['Microcontroller boards', 'Raspberry Pi boards', 'DC motors, servos and motor drivers', 'Sensor kits', 'Robot chassis, wheels and batteries', 'Programming computers'],
        'skills': ['Embedded programming', 'Motor control and motion logic', 'Sensor integration', 'Basic control concepts', 'Hardware debugging and wiring'],
        'careers': ['Robotics technician', 'Automation technician', 'Mechatronics technician', 'Embedded systems technician', 'Robotics field support engineer'],
    },
    'CAD': {
        'resources': ['High-performance computers', 'Professional CAD software', '3D printer', 'Digital calipers'],
        'skills': ['2D sketching', '3D modelling', 'Assemblies', 'Technical drawings', 'Export for manufacturing'],
        'careers': ['CAD technician', 'Mechanical design assistant', 'Product design technician', 'Architectural CAD technician', 'Prototyping technician'],
    },
    'AI': {
        'resources': ['Computers', 'Python', 'ML libraries', 'Notebook environment', 'Optional GPU'],
        'skills': ['Python for AI', 'Data preparation', 'Model training', 'Evaluation', 'Basic deep learning concepts'],
        'careers': ['Junior AI engineer', 'Junior ML engineer', 'Computer vision engineer', 'AI solutions developer', 'Applied AI research assistant'],
    },
    # Add the remaining pathways as in your original code
}

ALL_PATHWAYS = list(PATHWAY_DATA.keys())
DEFAULT_SETTINGS = {
    'theme': 'light',
    'price_per_student': 280000,
    'ratio_young': 15,
    'ratio_older': 25,
    'pathway_weeks': {p: 12 for p in ALL_PATHWAYS},
    'pathway_computer_ratio': {p: 2 for p in ALL_PATHWAYS},
    'pathway_kit_ratio': {p: 4 for p in ALL_PATHWAYS},
}

# -------------------
# Utility functions
# -------------------
def get_settings():
    if 'settings' not in session:
        session['settings'] = DEFAULT_SETTINGS.copy()
        session['settings']['pathway_weeks'] = DEFAULT_SETTINGS['pathway_weeks'].copy()
        session['settings']['pathway_computer_ratio'] = DEFAULT_SETTINGS['pathway_computer_ratio'].copy()
        session['settings']['pathway_kit_ratio'] = DEFAULT_SETTINGS['pathway_kit_ratio'].copy()
    return session['settings']

def calc_teachers(count, ratio):
    if count == 0 or ratio == 0:
        return 0
    return math.ceil(count / ratio)

def calc_learning_time(pathways, weeks_map):
    if not pathways:
        return 0
    batches = [pathways[i:i+2] for i in range(0, len(pathways), 2)]
    total = 0
    for batch in batches:
        total += max(weeks_map.get(p, 12) for p in batch)
    return total

def calc_resources(total_students, ratio):
    if ratio == 0:
        return 0
    return math.ceil(total_students / ratio)

# -------------------
# Routes
# -------------------
@app.route('/')
def index():
    return redirect(url_for('input_page'))

@app.route('/input', methods=['GET', 'POST'])
def input_page():
    settings = get_settings()
    if request.method == 'POST':
        mode = request.form.get('student_mode', 'both')
        students_young = int(request.form.get('students_young', 0) or 0)
        students_older = int(request.form.get('students_older', 0) or 0)
        pathway_mode = request.form.get('pathway_mode', 'ignore')
        selected_pathways = []
        if pathway_mode == 'all':
            selected_pathways = ALL_PATHWAYS[:]
        elif pathway_mode == 'specific':
            selected_pathways = request.form.getlist('pathways')

        session['last_input'] = {
            'student_mode': mode,
            'students_young': students_young,
            'students_older': students_older,
            'pathway_mode': pathway_mode,
            'selected_pathways': selected_pathways,
        }
        session.modified = True
        return redirect(url_for('output_page'))

    last = session.get('last_input', {})
    return render_template('input.html', settings=settings, pathways=ALL_PATHWAYS, last=last)

@app.route('/output')
def output_page():
    settings = get_settings()
    if 'last_input' not in session:
        return redirect(url_for('input_page'))

    data = session['last_input']
    mode = data['student_mode']
    sy = data['students_young'] if mode in ('young', 'both') else 0
    so = data['students_older'] if mode in ('older', 'both') else 0
    total = sy + so

    ratio_young = settings['ratio_young']
    ratio_older = settings['ratio_older']
    teachers_young = calc_teachers(sy, ratio_young)
    teachers_older = calc_teachers(so, ratio_older)
    total_teachers = teachers_young + teachers_older

    price = settings['price_per_student']
    total_fee = total * price

    selected_pathways = data['selected_pathways']
    weeks_map = settings['pathway_weeks']
    learning_time = calc_learning_time(selected_pathways, weeks_map)

    pathway_details = []
    for p in selected_pathways:
        comp_ratio = settings['pathway_computer_ratio'].get(p, 2)
        kit_ratio = settings['pathway_kit_ratio'].get(p, 4)
        computers = calc_resources(total, comp_ratio)
        kits = calc_resources(total, kit_ratio)
        pathway_details.append({
            'name': p,
            'weeks': weeks_map.get(p, 12),
            'computers': computers,
            'kits': kits,
            'comp_ratio': comp_ratio,
            'kit_ratio': kit_ratio,
            'resources': PATHWAY_DATA[p]['resources'],
            'skills': PATHWAY_DATA[p]['skills'],
            'careers': PATHWAY_DATA[p]['careers'],
        })

    return render_template('output.html',
        settings=settings,
        total=total,
        sy=sy,
        so=so,
        teachers_young=teachers_young,
        teachers_older=teachers_older,
        total_teachers=total_teachers,
        total_fee=total_fee,
        pathway_mode=data['pathway_mode'],
        selected_pathways=selected_pathways,
        learning_time=learning_time,
        pathway_details=pathway_details,
        mode=mode,
    )

@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    settings = get_settings()
    if request.method == 'POST':
        settings['theme'] = request.form.get('theme', 'light')
        settings['price_per_student'] = int(request.form.get('price_per_student', 280000) or 280000)
        settings['ratio_young'] = int(request.form.get('ratio_young', 15) or 15)
        settings['ratio_older'] = int(request.form.get('ratio_older', 25) or 25)

        for p in ALL_PATHWAYS:
            key = p.replace(' ', '_').lower()
            settings['pathway_weeks'][p] = int(request.form.get(f'weeks_{key}', 12) or 12)
            settings['pathway_computer_ratio'][p] = int(request.form.get(f'comp_{key}', 2) or 2)
            settings['pathway_kit_ratio'][p] = int(request.form.get(f'kit_{key}', 4) or 4)

        session['settings'] = settings
        session.modified = True
        return redirect(url_for('settings_page'))

    return render_template('settings.html', settings=settings, pathways=ALL_PATHWAYS)

# -------------------
# No app.run()!
# Vercel will handle the serverless deployment
# -------------------
