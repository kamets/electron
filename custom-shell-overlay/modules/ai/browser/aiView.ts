/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/

import { IViewletViewOptions } from '../../../browser/parts/views/viewsViewlet.js';
import { ViewPane } from '../../../browser/parts/views/viewPane.js';
import { IKeybindingService } from '../../../../platform/keybinding/common/keybinding.js';
import { IContextMenuService, IContextViewService } from '../../../../platform/contextview/browser/contextView.js';
import { IConfigurationService } from '../../../../platform/configuration/common/configuration.js';
import { IContextKeyService } from '../../../../platform/contextkey/common/contextkey.js';
import { IInstantiationService } from '../../../../platform/instantiation/common/instantiation.js';
import { IOpenerService } from '../../../../platform/opener/common/opener.js';
import { IThemeService } from '../../../../platform/theme/common/themeService.js';
import { ITelemetryService } from '../../../../platform/telemetry/common/telemetry.js';
import { IViewDescriptorService } from '../../../common/views.js';
import * as DOM from '../../../../base/browser/dom.js';
import { Button } from '../../../../base/browser/ui/button/button.js';
import { InputBox } from '../../../../base/browser/ui/inputbox/inputBox.js';
import { ITerminalService } from '../../../contrib/terminal/browser/terminal.js';

export class AIView extends ViewPane {

    private chatHistory: HTMLElement | undefined;

    constructor(
        options: IViewletViewOptions,
        @IKeybindingService keybindingService: IKeybindingService,
        @IContextMenuService contextMenuService: IContextMenuService,
        @IContextViewService private readonly contextViewService: IContextViewService,
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

        container.classList.add('ai-view');
        const content = DOM.append(container, DOM.$('.ai-content'));
        content.style.padding = '10px';
        content.style.display = 'flex';
        content.style.flexDirection = 'column';
        content.style.height = '100%';
        content.style.gap = '10px';

        // Chat History
        this.chatHistory = DOM.append(content, DOM.$('.chat-history'));
        this.chatHistory!.style.flex = '1';
        this.chatHistory!.style.overflowY = 'auto';
        this.chatHistory!.style.border = '1px solid #333';
        this.chatHistory!.style.padding = '5px';
        this.chatHistory!.innerText = 'Local AI Ready. Type to interact...';

        // Input Area
        const inputContainer = DOM.append(content, DOM.$('.input-container'));
        inputContainer.style.display = 'flex';
        inputContainer.style.gap = '5px';

        const inputBox = new InputBox(inputContainer, this.contextViewService, { placeholder: 'Ask the model...' });
        inputBox.element.style.flex = '1';

        const sendBtn = new Button(inputContainer, { title: 'Send' });
        sendBtn.label = 'Send';
        sendBtn.onDidClick(() => {
            const val = inputBox.value;
            if (val) {
                this.addMessage('User: ' + val);
                this.sendMessageToAI(val);
                inputBox.value = '';
            }
        });
    }

    private addMessage(text: string) {
        if (this.chatHistory) {
            const msg = DOM.append(this.chatHistory, DOM.$('.msg'));
            msg.innerText = text;
            msg.style.marginBottom = '5px';
            msg.style.borderBottom = '1px solid #444';
            this.chatHistory.scrollTop = this.chatHistory.scrollHeight;
        }
    }

    private async sendMessageToAI(text: string) {
        this.addMessage('User: ' + text);

        try {
            const response = await fetch('http://localhost:5000/v1/chat/completions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: "local-model",
                    messages: [{ role: "user", content: text }]
                })
            });

            if (!response.ok) {
                this.addMessage('Error: Agent seems offline. Did you launch it?');
                return;
            }

            const data = await response.json();
            const reply = data.choices?.[0]?.message?.content || "No response received.";
            this.addMessage('Agent: ' + reply);

        } catch (e) {
            this.addMessage('Error: Could not connect to localhost:5000. Launch the agent first.');
        }
    }

    private async launchAgent() {
        const instance = await this.terminalService.createTerminal({ name: 'DeepAgent Server' });
        instance.show();
        instance.sendText('bash ./custom-shell-overlay/modules/ai/scripts/launch_agent.sh');
    }
}
