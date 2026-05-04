import os
from bs4 import BeautifulSoup
import re

def main():
    dashboard_path = '/home/gotaro/Videos/paguyuban/dashboard.html'
    template_path = '/home/gotaro/Videos/paguyuban/template.html'
    output_path = '/home/gotaro/Videos/paguyuban/dashboard_new.html'

    with open(dashboard_path, 'r', encoding='utf-8') as f:
        soup_dash = BeautifulSoup(f.read(), 'html.parser')

    with open(template_path, 'r', encoding='utf-8') as f:
        soup_temp = BeautifulSoup(f.read(), 'html.parser')

    # Get custom styles from dashboard
    style = soup_dash.find('style')
    if style:
        # We might want to filter out body background and sidebar styles that conflict
        style_text = style.string
        # Remove `.sidebar` and `.main-content` CSS to rely on SB admin
        style_text = re.sub(r'\.sidebar\s*\{[^}]*\}', '', style_text)
        style_text = re.sub(r'\.main-content\s*\{[^}]*\}', '', style_text)
        style.string = style_text
        soup_temp.head.append(style)
        
    # Get custom js script
    scripts = soup_dash.find_all('script')
    custom_scripts = [s for s in scripts if not s.get('src')]
    
    # We will modify the custom script to generate SB Admin sidebar links
    for s in custom_scripts:
        if s.string:
            s_text = s.string
            # Update buildSidebar to use SB Admin classes
            s_text = s_text.replace(
                """  const nav = document.getElementById('sidebarNav');
  nav.innerHTML = `<div class="nav-group-title">Menu Utama</div>` +
    navItems.filter(i => i.show).map(i => `
      <div class="nav-item" id="nav-${i.id}" onclick="showPage('${i.id}')">
        <span class="icon">${i.icon}</span> ${i.label}
      </div>
    `).join('');""",
                """  const nav = document.getElementById('accordionSidenav');
  nav.innerHTML = `<div class="sidenav-menu-heading">Menu Utama</div>` +
    navItems.filter(i => i.show).map(i => `
      <a class="nav-link" href="#" id="nav-${i.id}" onclick="showPage('${i.id}')">
        <div class="nav-link-icon">${i.icon}</div>
        ${i.label}
      </a>
    `).join('');"""
            )
            # Update active class toggling
            s_text = s_text.replace("document.querySelectorAll('.nav-item')", "document.querySelectorAll('.nav-link')")
            s.string = s_text

    # Get login page
    login_page = soup_dash.find(id='loginPage')
    
    # Get modals and toast
    modals = soup_dash.find_all('div', class_='modal-overlay')
    toast = soup_dash.find(id='toastContainer')

    # Wrap them in a div#dashboard
    topnav = soup_temp.find('nav', class_='topnav')
    layout_sidenav = soup_temp.find(id='layoutSidenav')
    
    dash_wrapper = soup_temp.new_tag('div', id='dashboard', style='display:none;')
    if topnav:
        dash_wrapper.append(topnav.extract())
    if layout_sidenav:
        dash_wrapper.append(layout_sidenav.extract())
        
    soup_temp.body.insert(0, login_page)
    soup_temp.body.insert(1, dash_wrapper)
    
    for m in modals:
        soup_temp.body.append(m)
    if toast:
        soup_temp.body.append(toast)

    main_tag = soup_temp.find('main')
    if main_tag:
        main_tag.clear()
        
        # SB Admin container
        container = soup_temp.new_tag('div', **{'class': 'container-xl px-4 mt-4'})
        main_tag.append(container)
        
        # We need to add the page title header from dashboard.html
        header_div = soup_temp.new_tag('div', style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;")
        h2 = soup_temp.new_tag('h2', id='pageTitle', style='margin:0;')
        h2.string = 'Dashboard'
        date_div = soup_temp.new_tag('div', id='dateDisplay', style='color:var(--text-muted);font-size:14px;')
        header_div.append(h2)
        header_div.append(date_div)
        container.append(header_div)

        pages = soup_dash.find_all('div', class_='page')
        for page in pages:
            container.append(page)

    for s in custom_scripts:
        soup_temp.body.append(s)

    # Convert native table classes to bootstrap table classes
    for table in soup_temp.find_all('table', class_='data-table'):
        table['class'] = table.get('class', []) + ['table', 'table-bordered', 'table-hover']

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(str(soup_temp))

if __name__ == '__main__':
    main()
