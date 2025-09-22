import data from '../../template.yaml';
import 'katex/dist/katex.min.css';

// Import CSS synchronously based on theme
if (data.theme === 'dark') {
  import('../scss/dark-theme.scss');
} else {
  import('../scss/theme.scss');
}

import UIkit from 'uikit';
import Icons from 'uikit/dist/js/uikit-icons';

// Initialize UIKit immediately
UIkit.use(Icons);
