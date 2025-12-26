/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/

import { IViewletViewOptions } from '../../../browser/parts/views/viewsViewlet.js';
import { ViewPane } from '../../../browser/parts/views/viewPane.js';
import { IKeybindingService } from '../../../../platform/keybinding/common/keybinding.js';
import { IContextMenuService } from '../../../../platform/contextview/browser/contextView.js';
import { IConfigurationService } from '../../../../platform/configuration/common/configuration.js';
import { IContextKeyService } from '../../../../platform/contextkey/common/contextkey.js';
import { IInstantiationService } from '../../../../platform/instantiation/common/instantiation.js';
import { IOpenerService } from '../../../../platform/opener/common/opener.js';
import { IThemeService } from '../../../../platform/theme/common/themeService.js';
import { ITelemetryService } from '../../../../platform/telemetry/common/telemetry.js';
import { IViewDescriptorService } from '../../../common/views.js';
import * as DOM from '../../../../base/browser/dom.js';
import { Button } from '../../../../base/browser/ui/button/button.js';
import { ITerminalService } from '../../../contrib/terminal/browser/terminal.js';

export class FinancialView extends ViewPane {

    constructor(
        options: IViewletViewOptions,
        @IKeybindingService keybindingService: IKeybindingService,
        @IContextMenuService contextMenuService: IContextMenuService,
        @IConfigurationService configurationService: IConfigurationService,
        @IContextKeyService contextKeyService: IContextKeyService,
        @IInstantiationService instantiationService: IInstantiationService,
        @IViewDescriptorService viewDescriptorService: IViewDescriptorService,
        @IOpenerService openerService: IOpenerService,
        @IThemeService themeService: IThemeService,
        @ITelemetryService telemetryService: ITelemetryService,
        @ITerminalService private readonly terminalService: ITerminalService
    ) {
        super(options, keybindingService, contextMenuService, configurationService, contextKeyService, viewDescriptorService, instantiationService, openerService, themeService, telemetryService);
    }

    protected override renderBody(container: HTMLElement): void {
        super.renderBody(container);

        container.classList.add('financial-view');
        const content = DOM.append(container, DOM.$('.financial-content'));
        content.style.padding = '20px';
        content.style.display = 'flex';
        content.style.flexDirection = 'column';
        content.style.gap = '10px';

        // Title
        const title = DOM.append(content, DOM.$('h2'));
        title.innerText = 'Investigative Actions';
        title.style.marginBottom = '20px';

        // Button 1: Run Analysis
        this.createButton(content, 'Run Forensic Analysis', () => this.runPythonScript('analysis.py'));

        // Button 2: Convert to CSV
        this.createButton(content, 'Convert Docs to CSV', () => this.runPythonScript('convert_to_csv.py'));

        // Button 3: Local LLM Chat (Placeholder)
        this.createButton(content, 'Ask Local AI', () => this.runPythonScript('chat_model.py'));

        // Button 4: Link External Libraries (New)
        this.createButton(content, 'Link External Libraries', () => this.runLinkLibsScript());
    }

    private createButton(container: HTMLElement, label: string, onClick: () => void) {
        const button = new Button(container, { title: label, supportIcons: true });
        button.label = label;
        button.element.style.maxWidth = '300px';
        button.onDidClick(onClick);
    }

    private async runLinkLibsScript() {
        const instance = await this.terminalService.createTerminal({ name: 'Library Setup' });
        instance.show();
        instance.sendText('bash ./custom-shell-overlay/modules/financial/scripts/setup_libs.sh');
    }

    private async runPythonScript(scriptName: string) {
        const instance = await this.terminalService.createTerminal({ name: 'InvestigativeOS Console' });
        instance.show();
        // Assuming scripts are in a 'scripts' folder relative to the workspace or a fixed path
        // For now, echoing to demonstrate linkage
        instance.sendText(`echo "Running ${scriptName}..."`);
        instance.sendText(`# python3 ./scripts/${scriptName}`);
    }
}
