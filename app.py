from flask import Flask, render_template, request, redirect, url_for, session
import math
#hello
app = Flask(__name__)
app.secret_key = 'futurefundi-secret-2024'

PATHWAY_DATA = {
    'Robotics': {
        'resources': [
            'Microcontroller boards',
            'Single-board computers from Raspberry Pi Foundation',
            'DC motors, servos and motor drivers',
            'Sensor kits (ultrasonic, IMU, line sensors, encoders)',
            'Robot chassis, wheels and batteries',
            'Programming computers',
        ],
        'skills': [
            'Embedded programming',
            'Motor control and motion logic',
            'Sensor integration',
            'Basic control concepts (PID awareness)',
            'Hardware debugging and wiring',
        ],
        'careers': [
            'Robotics technician',
            'Automation technician',
            'Mechatronics technician',
            'Embedded systems technician',
            'Robotics field support engineer',
        ],
    },
    'CAD': {
        'resources': [
            'High-performance computers',
            'Professional CAD software (education licenses)',
            '3D printer for prototyping',
            'Digital calipers and measuring tools',
        ],
        'skills': [
            '2D sketching and constraints',
            '3D solid modelling',
            'Assemblies',
            'Technical drawings',
            'Export for manufacturing and 3D printing',
        ],
        'careers': [
            'CAD technician',
            'Mechanical design assistant',
            'Product design technician',
            'Architectural CAD technician',
            'Prototyping / 3D printing technician',
        ],
    },
    'AI': {
        'resources': [
            'Computers or laptops',
            'Python development environment',
            'Machine learning and deep-learning libraries',
            'Notebook environment',
            'Optional GPU workstation',
        ],
        'skills': [
            'Python for AI',
            'Data preparation',
            'Model training and testing',
            'Model evaluation',
            'Basic deep learning concepts',
        ],
        'careers': [
            'Junior AI engineer',
            'Junior machine learning engineer',
            'Computer vision engineer (junior)',
            'AI solutions developer',
            'Applied AI research assistant',
        ],
    },
    'Electronics': {
        'resources': [
            'Soldering stations',
            'Digital multimeters',
            'Bench power supplies',
            'One shared oscilloscope',
            'Breadboards and jumper wires',
            'Component stock (resistors, capacitors, diodes, transistors, regulators, sensors)',
            'Microcontroller development boards from Arduino',
        ],
        'skills': [
            'Reading electronic schematics',
            'Circuit construction',
            'Measurement and testing',
            'Fault finding and repair',
            'Embedded hardware interfacing',
        ],
        'careers': [
            'Electronics technician',
            'Embedded systems technician',
            'IoT technician',
            'PCB assembly and test technician',
            'Instrumentation technician',
        ],
    },
    'Data Science': {
        'resources': [
            'Computer lab',
            'Python environment',
            'Data analysis and visualisation tools',
            'SQL and database tools',
        ],
        'skills': [
            'Data cleaning and preparation',
            'Exploratory data analysis',
            'Data visualisation',
            'Statistics for data analysis',
            'Introductory machine learning',
        ],
        'careers': [
            'Data analyst',
            'Business intelligence analyst',
            'Junior data scientist',
            'Data technician',
            'Research data assistant',
        ],
    },
    'Web Development': {
        'resources': [
            'Computers',
            'Code editors',
            'Browsers and developer tools',
            'Local development servers',
            'Test hosting environment',
        ],
        'skills': [
            'HTML, CSS and JavaScript',
            'Backend programming',
            'API development',
            'Database integration',
            'Authentication and deployment',
        ],
        'careers': [
            'Front-end web developer',
            'Back-end web developer',
            'Full-stack web developer',
            'Web application support engineer',
            'Junior software engineer',
        ],
    },
    'App Development': {
        'resources': [
            'Computers',
            'Mobile development SDKs',
            'Device emulators',
            'Real Android smartphones for testing',
        ],
        'skills': [
            'Mobile UI design',
            'Application logic and navigation',
            'API integration',
            'Local data storage',
            'App packaging and deployment',
        ],
        'careers': [
            'Mobile app developer',
            'Mobile software engineer',
            'Junior mobile developer',
            'App UI/UX developer',
            'Mobile solutions technician',
        ],
    },
    'Cyber Security': {
        'resources': [
            'Computer lab',
            'Virtual machines',
            'Isolated practice network',
            'Network monitoring and security tools',
            'Vulnerable test systems',
            'Ethical and legal usage policy for the lab',
        ],
        'skills': [
            'Networking fundamentals',
            'Linux system administration',
            'Vulnerability identification',
            'Web and system security basics',
            'Incident response concepts',
        ],
        'careers': [
            'Cybersecurity technician',
            'SOC analyst (junior)',
            'IT security support officer',
            'Network security technician',
            'Vulnerability assessment assistant',
        ],
    },
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


if __name__ == '__main__':
    app.run(debug=True)
