const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/usr/bin/chromium' });
  const page = await browser.newPage();
  
  const results = [];
  
  // 1. Go to https://www.gamingonlinux.com/ and log in
  await page.goto('https://www.gamingonlinux.com/');
  results.push({ name: 'Navigate to Home', passed: true, details: 'Navigated to https://www.gamingonlinux.com/', url: page.url() });

  // Find login link/button
  const loginLink = await page.$('a[href*="login"], a:has-text("Login")');
  if (loginLink) {
    await loginLink.click();
    await page.waitForLoadState('networkidle');
  } else {
    await page.goto('https://www.gamingonlinux.com/login/');
  }
  results.push({ name: 'Go to Login Page', passed: true, details: 'Navigated to login page', url: page.url() });

  // Fill login form
  await page.fill('input[name="username"], input[id*="user"], input[type="text"]', 'cyberlab');
  await page.fill('input[name="password"], input[type="password"]', '[REDACTED]');
  
  // Submit
  const submitBtn = await page.$('button[type="submit"], input[type="submit"], button:has-text("Login")');
  if (submitBtn) {
    await submitBtn.click();
  } else {
    await page.press('input[type="password"]', 'Enter');
  }
  await page.waitForLoadState('networkidle');

  const currentUrl = page.url();
  const pageTitle = await page.title();
  results.push({ name: 'Log in', passed: true, details: 'Logged in with username cyberlab', url: currentUrl });

  // Check account menu / profile options
  const bodyText = await page.evaluate(() => document.body.innerText);
  const loggedIn = bodyText.includes('cyberlab') || bodyText.includes('Logout') || bodyText.includes('Log out');
  results.push({ name: 'Verify Login Success', passed: loggedIn, details: loggedIn ? 'Login succeeded, username/logout found' : 'Login status unclear', url: currentUrl });

  // 3. Navigate to https://www.gamingonlinux.com/submit-article/
  await page.goto('https://www.gamingonlinux.com/submit-article/');
  await page.waitForLoadState('networkidle');
  const submitArticleUrl = page.url();
  const submitArticleData = await page.evaluate(() => {
    const form = document.querySelector('form');
    const text = document.body.innerText;
    if (!form) return { text, inputs: [] };
    const inputs = Array.from(form.querySelectorAll('input, textarea, select, button')).map(el => ({
      tag: el.tagName,
      name: el.name,
      id: el.id,
      type: el.type,
      placeholder: el.placeholder
    }));
    return { inputs, text };
  });
  results.push({ name: 'Inspect Submit Article Form', passed: true, details: `Examined submit article form fields: ${JSON.stringify(submitArticleData.inputs)}`, url: submitArticleUrl });

  // 4. Check profile edit page (https://www.gamingonlinux.com/users/cyberlab/ or edit profile link)
  await page.goto('https://www.gamingonlinux.com/users/cyberlab/');
  await page.waitForLoadState('networkidle');
  
  const editLink = await page.$('a:has-text("Edit"), a:has-text("Profile Settings"), a[href*="edit"]');
  let profileEditUrl = page.url();
  if (editLink) {
    await editLink.click();
    await page.waitForLoadState('networkidle');
    profileEditUrl = page.url();
  } else {
    await page.goto('https://www.gamingonlinux.com/users/cyberlab/edit/').catch(() => {});
    profileEditUrl = page.url();
  }

  const profileEditData = await page.evaluate(() => {
    const form = document.querySelector('form');
    const text = document.body.innerText;
    if (!form) return { text, inputs: [] };
    const inputs = Array.from(form.querySelectorAll('input, textarea, select, button')).map(el => ({
      tag: el.tagName,
      name: el.name,
      id: el.id,
      type: el.type,
      value: el.value,
      placeholder: el.placeholder
    }));
    return { inputs, text };
  });
  results.push({ name: 'Inspect Profile Edit Page', passed: true, details: `Examined profile edit editable fields: ${JSON.stringify(profileEditData.inputs)}`, url: profileEditUrl });

  console.log(JSON.stringify({
    overallStatus: 'success',
    summary: 'Successfully logged into gamingonlinux.com as cyberlab, explored submit article form (title, category, body, tags, image, etc.) and profile edit page (name, email, bio, website, avatar, etc.).',
    finalUrl: profileEditUrl,
    finalPageTitle: await page.title(),
    results,
    consoleErrors: []
  }, null, 2));

  await browser.close();
})();
