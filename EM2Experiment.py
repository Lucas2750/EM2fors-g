from psychopy import visual, core, event, data, gui
import random
import os
import sys # Til at afslutte programmet pænt ved annullering af dialog

# Definer stien til videos
VIDEO_DIR = 'Assets'
# Tider for agent-animation (baseret på din 25 sek. video)
T_START_IN = 0.0
T_END_IN = 3.5
T_START_OUT = 12.0
T_END_OUT = 15.0
T_START_IN_2 = 18.0
T_END_IN_2 = 21.0
VIDEO_LENGTH = 25.0

# Tidspunkt for væggen fjernes/responsen skal starte (ca. 22.5s)
RESPONSE_START_TIME = 22.5 
RESPONSE_DURATION = 2.5 # Responsvindue er 2.5 sekunder

# NY KONSTANT
NUM_BUFFER_TRIALS = 2 # Antal buffer forsøg i starten af hver blok

class EM2Experiment:
    def __init__(self):
        # Initialiser Subject ID og Navn som None
        self.subject_id = None 
        self.subject_name = None 

        # Indstil vindue og andre standardindstillinger
        self.win = None 
        
        self.clock = core.Clock()
        self.trial_data = []
        self.trial_num = 0
        self.num_trials_per_condition = 1  # 8 betingelser * 1 = 8 trials
        self.num_trials_per_block = 8
        self.num_blocks = 2 # Smurf + Self Agent
        self.num_practice_trials = 8 # 8 praksis trials 

        # Definer alle betingelser
        self.conditions = [
            {'agent_belief': True, 'Part_belief': True, 'Ball_present': True, 'condition': 'P+A+(+)'},
            {'agent_belief': True, 'Part_belief': True, 'Ball_present': False, 'condition': 'P+A+(-)'},
            {'agent_belief': True, 'Part_belief': False, 'Ball_present': False, 'condition': 'P-A+(-)'},
            {'agent_belief': True, 'Part_belief': False, 'Ball_present': True, 'condition': 'P-A+(+)'},
            {'agent_belief': False, 'Part_belief': True, 'Ball_present': True, 'condition': 'P+A-(+)'},
            {'agent_belief': False, 'Part_belief': True, 'Ball_present': False, 'condition': 'P+A-(-)'},
            {'agent_belief': False, 'Part_belief': False, 'Ball_present': False, 'condition': 'P-A-(-)'},
            {'agent_belief': False, 'Part_belief': False, 'Ball_present': True, 'condition': 'P-A-(+)'}
        ]

        # Spørgsmålene til spørgeskemaet
        self.questionnaire_questions = [
            "Jeg synes at avataren i denne blok lignede mig.",
            "Jeg havde en oplevelse af, at avataren i denne blok var mig.",
            "Jeg havde en oplevelse af, at avatarens identitet eller krop var en forlængelse af min egen.",
            "Jeg følte, at avataren repræsenterede mig selv.",
            "Jeg synes det var let at forestille mig situationen fra avatarens perspektiv.",
            "Jeg følte, at jeg automatisk tog avatarens perspektiv i opgaven.",
            "Jeg var opmærksom på avatarens overbevisning om, hvor bolden befandt sig."
        ]

        # Opret den fulde liste over forsøg for HVER blok (2 blokke * 8 forsøg + buffer)
        self.trials_list_block1 = self._create_shuffled_trials_list(include_buffer=True)
        self.trials_list_block2 = self._create_shuffled_trials_list(include_buffer=True)
        
        # Stimuli initialiseres senere i run_experiment()
        self.smurf_agent = None
        self.self_agent = None
        self.current_agent_stim = None
        self.name_stim = None 
        self.smurf_name_stim = None # NYT: Smølf navnet

    def get_subject_id(self):
        """Indsamler Subject ID og Navn ved hjælp af en dialogboks."""
        # Dialogboks med både ID og Navn
        dlg = gui.DlgFromDict(dictionary={'Subject ID (Indtast 4 cifre)': '', 'Dit navn:': ''}, 
                              title='Eksperiment Information')
        
        if dlg.OK:
            self.subject_id = dlg.dictionary['Subject ID (Indtast 4 cifre)']
            self.subject_name = dlg.dictionary['Dit navn:'] # Gemmer navnet
            
            # Validering af 4 cifre for ID
            if not (len(self.subject_id) == 4 and self.subject_id.isdigit()):
                print("FEJL: Subject ID skal være 4 cifre. Forsøger igen.")
                self.subject_id = self.get_subject_id() 
            
            return self.subject_id
        else:
            # Hvis brugeren trykker Annuller
            core.quit()
            sys.exit()

    def setup_visual_stimuli(self):
        """Opretter PsychoPy vinduet og stimuli efter ID er indsamlet."""
        if self.win is None:
            self.win = visual.Window([1280, 720], color='black', fullscr=True, monitor='testMonitor', units='pix') 
            
            # Opret agent billed stimuli (NY STØRRELSE: 200, 200)
            agent_size = (200, 200)
            self.smurf_agent = visual.ImageStim(self.win, image=os.path.join(VIDEO_DIR, 'smurf1.png'), 
                                                pos=[-1300, 0], size=agent_size)
            self.self_agent = visual.ImageStim(self.win, image=os.path.join(VIDEO_DIR, 'selfAgent.png'), 
                                               pos=[-1300, 0], size=agent_size)
            # Initialiser agenten der skal bruges i starten
            self.current_agent_stim = self.smurf_agent

            # NYT: Opret tekst-stimulus til at vise navnet
            if self.subject_name is None:
                self.subject_name = "Navn" 
            
            # Navn over Self-Agent (Y = 150 er over agenten med str. 200)
            self.name_stim = visual.TextStim(self.win, text=self.subject_name, 
                                             color='white', pos=[-1300, 150], height=30)
            
            # NYT: Navn over Smurf-Agent
            self.smurf_name_stim = visual.TextStim(self.win, text="SMØLF", 
                                                   color='white', pos=[-1300, 150], height=30)


    def _create_shuffled_trials_list(self, include_buffer=False):
        """Opretter en randomiseret liste af betingelser for en hel blok, inkl. buffer-trials."""
        condition_values = [cond['condition'] for cond in self.conditions]
        
        # Opretter den shufflede liste af MAIN trials
        trials_list = condition_values * self.num_trials_per_condition
        random.shuffle(trials_list)
        
        if include_buffer:
            # Vælger tilfældigt 2 trials (med genplacering) til at være buffer
            # Disse fjernes ikke fra hovedlisten, så der er buffer + 8 trials
            buffer_trials = random.choices(condition_values, k=NUM_BUFFER_TRIALS)
            
            # Tilføjer buffer trials FØRST i listen
            trials_list = buffer_trials + trials_list
            
        return trials_list

    def show_instructions(self):
        # Bruger nu self.win
        instructions = visual.TextStim(self.win, text="Velkommen til vores eksperiment!\n" \
        "\nDu vil blive vist en video af en bold der bevæger sig." \
        "\nDit job er at i slutningen af videoen skal du svare på om bolden er bag en væg.\n" \
        "\nTryk IKKE på noget hvis bolden IKKE er bag væggen, når væggen fjernes." \
        "\nTryk på 'SPACE/Mellemrum' når du ser bolden bag væggen, når væggen fjernes.\n" \
        "\nDu skal først svare på dette, når væggen er væk! Dette er vigtigt, så du skal sidde klar.\n" \
        "\nDet er tilfældigt om bolden er bag væggen eller ej." \
        "\nSvar så hurtigt og præcist som muligt.\n" \
        "\nTryk på ‘SPACE’ for at starte.", 
        color='white', wrapWidth=1200, height=30)
        instructions.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])

    def practice_instructions(self):
        # ... (Praksis instruktioner som før)
        practice_text = visual.TextStim(self.win, text="Nu vil du starte med nogle prøve forsøg." \
        "\nDisse vil hjælpe dig med at forstå opgaven bedre.\n" \
        "\nTryk på ‘SPACE’ for at starte.", color='white', wrapWidth=1200, height=30)
        practice_text.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])
    
    def _get_condition_details(self, condition_name):
        """Finder detaljerne for en betingelse baseret på betingelsesnavnet."""
        for cond in self.conditions:
            if cond['condition'] == condition_name:
                return cond
        return None

    def _animate_agent(self, current_time, agent_stim):
        """Beregn og sæt agentens position og horisontale flip baseret på videoens tidspunkt.
           Returnerer agentens aktuelle X-position.
        """
        
        # Start X pos. (uden for skærmen)
        x_start = -1300 
        # Slut X pos. (lidt til venstre for centrum)
        x_end = -250 
        
        current_x = x_start # Standard position

        # Funktion til lineær interpolation
        def lerp(start, end, t, t_start, t_end):
            if t < t_start or t > t_end:
                return None
            progress = (t - t_start) / (t_end - t_start)
            return start + progress * (end - start)

        # 1. Bevægelse ind (0.0s - 3.5s): Bevæger sig mod højre. FlipHoriz = False
        if current_time >= T_START_IN and current_time <= T_END_IN:
            agent_stim.flipHoriz = False 
            current_x = lerp(x_start, x_end, current_time, T_START_IN, T_END_IN)
            if current_x is not None:
                agent_stim.setPos([current_x, 0])
        # 2. Bevægelse ud (12.0s - 15.0s): Bevæger sig mod venstre. FlipHoriz = True
        elif current_time >= T_START_OUT and current_time <= T_END_OUT:
            agent_stim.flipHoriz = True 
            current_x = lerp(x_end, x_start, current_time, T_START_OUT, T_END_OUT)
            if current_x is not None:
                agent_stim.setPos([current_x, 0])
        # 3. Bevægelse ind (18.0s - 21.0s): Bevæger sig mod højre igen. FlipHoriz = False
        elif current_time >= T_START_IN_2 and current_time <= T_END_IN_2:
            agent_stim.flipHoriz = False 
            current_x = lerp(x_start, x_end, current_time, T_START_IN_2, T_END_IN_2)
            if current_x is not None:
                agent_stim.setPos([current_x, 0])
        # --- Fikserede positioner mellem bevægelser ---
        # Stoppet position (3.5s - 12.0s): Kigger mod højre. FlipHoriz = False
        elif current_time > T_END_IN and current_time < T_START_OUT:
            agent_stim.flipHoriz = False 
            current_x = x_end
            agent_stim.setPos([current_x, 0])
        # Uden for skærmen (15.0s - 18.0s)
        elif current_time >= T_END_OUT and current_time < T_START_IN_2:
            current_x = x_start
            agent_stim.setPos([current_x, 0])
        # Stoppet position (21.0s - 25.0s): Kigger mod højre. FlipHoriz = False
        elif current_time > T_END_IN_2 and current_time <= VIDEO_LENGTH:
            agent_stim.flipHoriz = False 
            current_x = x_end
            agent_stim.setPos([current_x, 0])
        # Uden for skærmen (Før start)
        else:
             current_x = x_start
             agent_stim.setPos([current_x, 0])

        return current_x # Returner X-positionen

    def run_trial(self, condition_name, practice=False, is_buffer=False):
        self.trial_num += 1
        condition_details = self._get_condition_details(condition_name)
        if not condition_details:
             print(f"Betingelse {condition_name} blev ikke fundet. Springer over.")
             return

        trial_type = condition_name
        ball_is_present = condition_details['Ball_present']
        
        # --- Video visning og Animation ---
        video_file = os.path.join(VIDEO_DIR, f'{condition_name}.mp4')
        
        if not os.path.exists(video_file):
            print(f"FEJL: Videofil '{video_file}' blev ikke fundet. Springer forsøg over.")
            error_stim = visual.TextStim(self.win, text=f"Fejl: Mangler {video_file}", color='red')
            error_stim.draw()
            self.win.flip()
            core.wait(2)
            # Log data selvom fil mangler
            self.trial_data.append({'trial_num': self.trial_num, 'trial_type': trial_type, 'response': 'FILE_MISSING', 'rt': -1, 
                                    'Ball_present': ball_is_present, 'Part_belief': condition_details['Part_belief'],
                                    'Agent_belief': condition_details['agent_belief'], 'Condition': condition_details['condition'],
                                    'Agent_Type': 'Smurf' if self.current_agent_stim == self.smurf_agent else 'Self',
                                    'is_buffer': is_buffer}) # NYT: is_buffer logges
            return

        stimulus = visual.MovieStim3(self.win, filename=video_file, size=(1280, 720), loop=False) 
        
        # Slet alle gamle events fra bufferen for at sikre præcise RT'er
        event.clearEvents()
        
        # Initialiser status- og responsvariabler
        responded = False
        response_start_time = 0.0
        response = 'None'
        rt = -1.0
        
        # --- Hovedforsøgsløkken ---
        self.clock.reset() # Nulstil klokken for forsøget
        
        while self.clock.getTime() <= VIDEO_LENGTH and stimulus.status != visual.FINISHED:
            current_time = self.clock.getTime()
            
            # 1. Tegn videoen og agenten (gælder for hele videoen)
            stimulus.draw()
            if current_time is not None:
                # Gemmer X-positionen, som _animate_agent returnerer
                agent_x = self._animate_agent(current_time, self.current_agent_stim)
                self.current_agent_stim.draw()
                
                # Håndter Navne-stimulus (svæver over agenten)
                if self.current_agent_stim == self.self_agent:
                    self.name_stim.setPos([agent_x, 150]) # Sæt navnet over Self-Agent
                    self.name_stim.draw()
                else: # Må være Smurf-agenten
                    self.smurf_name_stim.setPos([agent_x, 150]) # Sæt navnet over Smurf
                    self.smurf_name_stim.draw()
                
            # 2. Responsvinduet (starter ved 22.5s)
            if current_time >= RESPONSE_START_TIME and not responded:
                # Start RT-målingen præcist ved 22.5s
                if response_start_time == 0.0:
                    response_start_time = current_time 
                
                # Check for tryk
                keys = event.getKeys(keyList=['space', 'escape']) 
                
                if keys is not None:
                    if 'escape' in keys:
                        self.quit_experiment()
                    elif 'space' in keys:
                        responded = True
                        response = 'space'
                        rt = current_time - response_start_time
                        # Bryd løkken her, hvis der er svaret med 'space'
                        break 
                
                # Håndtering af Timeouts
                if not responded and current_time >= (response_start_time + RESPONSE_DURATION):
                    responded = True
                    rt = RESPONSE_DURATION # 2.5 sekunder
                    if not ball_is_present:
                        response = 'no_press'
                    else:
                        response = 'missed'
                    # SLUT: Bryd løkken uanset om det er 'no_press' eller 'missed'
                    break 

            # Tegn det hele på skærmen
            self.win.flip()
            
        # NULSTIL videoen, så den ikke fortsætter i baggrunden
        if stimulus.status != visual.FINISHED:
            stimulus.stop()


        # --- Log trial data efter videoafslutning ---
        # Sikkerhedscheck for ikke-besvaret forsøg
        if not responded:
            rt = RESPONSE_DURATION
            if not ball_is_present:
                response = 'no_press'
            else:
                response = 'missed'


        self.trial_data.append({
            'trial_num': self.trial_num,
            'trial_type': trial_type,
            'response': response,
            'rt': rt,
            'Ball_present': condition_details['Ball_present'],
            'Part_belief': condition_details['Part_belief'],
            'Agent_belief': condition_details['agent_belief'],
            'Condition': condition_details['condition'],
            'Agent_Type': 'Smurf' if self.current_agent_stim == self.smurf_agent else 'Self',
            'is_buffer': is_buffer # NYT: Log buffer-status
        })
        
        # Slet alle eventuelle resterende events fra bufferen
        event.clearEvents()
        
        # Fikseringskors (ITI)
        fixation = visual.TextStim(self.win, text='+', color='white', height=50)
        fixation.draw()
        self.win.flip()
        core.wait(1.0) 

    def practice_trials(self):
        # ... (Praksis forsøg som før)
        practice_list = [cond['condition'] for cond in self.conditions] * (self.num_practice_trials // len(self.conditions))
        random.shuffle(practice_list)
        
        # Denne løkke kører nu KUN 8 gange (8 betingelser * 1 gentagelse)
        for condition_name in practice_list:
            # I praksis bruges Smurfen som standard
            self.current_agent_stim = self.smurf_agent
            # buffer=False da det er praksis
            self.run_trial(condition_name, practice=True, is_buffer=False) 
            
        self.trial_num = 0
        self.trial_data = [] # Fjern praksis data
        
        end_practice_text = visual.TextStim(self.win, text="Du har nu gennemført prøveforsøgene." \
        "\nTryk på ‘SPACE’ for at starte hovedeksperimentet.", color='white', wrapWidth=1200, height=30)
        end_practice_text.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])
        
    def _block_transition(self, block_num):
        """Viser en pausebesked mellem blokkene."""
        # Denne funktion er designet til at vise info om den *kommende* blok
        agent_type = f"Self-Agent ({self.subject_name})" 
        
        transition_text = visual.TextStim(self.win, text=f"Forbered dig på BLOK 2." \
        f"\nI denne blok skal du observere: {agent_type}." \
        "\nTag en kort pause.\n\nTryk på ‘SPACE’ for at fortsætte.", color='white', wrapWidth=1200, height=30)
        transition_text.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])

    # RETTET: block_num tilføjet som argument
    def run_block(self, block_num, trials_list, agent_stim):
        """Kører en hel eksperimentblok."""
        self.current_agent_stim = agent_stim
        
        for i, condition_name in enumerate(trials_list):
            # Bestem om det er et buffer trial (de første NUM_BUFFER_TRIALS i listen)
            is_buffer_trial = i < NUM_BUFFER_TRIALS
            
            self.run_trial(condition_name, practice=False, is_buffer=is_buffer_trial)

    def questionnaire_block(self, block_num):
        """Kører spørgeskemaet og logger svarene."""
        
        # Bestem hvilken agent der lige er brugt
        agent_type = "Smurf" if block_num == 1 else "Self"
        
        # Instruktioner
        instructions = visual.TextStim(self.win, text=
                                        "Du skal nu svare på en række udsagn, der relaterer sig til den blok, du lige har gennemført.\n" \
                                        "\nDu bliver præsenteret for et udsagn og skal derefter angive" \
                                        "\nhvor enig du er i det givne udsagn på en skala fra 1-7.\n" \
                                        "\n**1 = helt uenig og 7 = helt enig**"
                                        "\n\nTryk på ‘SPACE’ for at komme videre", 
        color='white', wrapWidth=1200, height=30)
        instructions.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])

        # Skala tekst (vises på alle spørgsmål)
        scale_text = visual.TextStim(self.win, text="**1 = Helt uenig** **7 = Helt enig**", 
                                     pos=[0, -300], height=25, color='gray')
        
        # Input/feedback tekst
        response_text_stim = visual.TextStim(self.win, text="", pos=[0, -150], height=40, color='yellow')
        
        for q_idx, question_text in enumerate(self.questionnaire_questions):
            question_stim = visual.TextStim(self.win, text=f"Udsagn {q_idx + 1}/{len(self.questionnaire_questions)}:\n\n{question_text}", 
                                            pos=[0, 0], height=35, color='white', wrapWidth=1000)
            
            valid_response = False
            response_str = ""
            
            while not valid_response:
                # 1. Tegn stimuli
                question_stim.draw()
                scale_text.draw()
                response_text_stim.setText(f"Svar (1-7) eller Esc: {response_str}")
                response_text_stim.draw()
                self.win.flip()
                
                # 2. Hent taster
                keys = event.getKeys(keyList=['1', '2', '3', '4', '5', '6', '7', 'return', 'backspace', 'escape'])
                
                if keys:
                    key = keys[0]
                    
                    if key in ['1', '2', '3', '4', '5', '6', '7']:
                        # Tillad kun ét ciffer
                        if len(response_str) == 0:
                            response_str = key
                    
                    elif key == 'backspace':
                        response_str = "" 
                        
                    elif key == 'return':
                        if response_str in ['1', '2', '3', '4', '5', '6', '7']:
                            # Svaret er gyldigt
                            valid_response = True
                            
                            # Log data
                            self.trial_data.append({
                                'trial_num': self.trial_num,
                                'trial_type': 'Questionnaire',
                                'Agent_Type': agent_type,
                                'Question_ID': q_idx + 1,
                                'Question_Text': question_text,
                                'Questionnaire_Response': int(response_str),
                                # Sæt N/A for Trial-specifikke felter
                                'is_buffer': 'N/A', 
                                'response': 'N/A',
                                'rt': 'N/A',
                                'Ball_present': 'N/A',
                                'Part_belief': 'N/A',
                                'Agent_belief': 'N/A',
                                'Condition': 'N/A'
                            })
                            # Tæl op for at sikre unikke rækkenumre i datafilen
                            self.trial_num += 1 
                        else:
                            # Visuel feedback om ugyldigt input
                            response_str = ""
                            
                    elif key == 'escape':
                        self.quit_experiment()
                        
            # Kort pause mellem spørgsmål
            core.wait(0.5)
        
        # Vis bekræftelse
        complete_text = visual.TextStim(self.win, text="Spørgeskemaet er færdigt.\n\nTryk på 'SPACE' for at fortsætte.", color='white')
        complete_text.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])

    
    def run_experiment(self):
        # 1. INDSAMLE SUBJECT ID OG NAVN FØR VINDUE ÅBNES
        self.get_subject_id()
        
        # 2. OPSÆT VINDUE OG STIMULI
        self.setup_visual_stimuli()
        
        # 3. KØR EKSPERIMENT
        
        # Vis instruktioner
        self.show_instructions()
        
        # Kør praksis (bruger Smurf Agent)
        self.practice_instructions()
        self.practice_trials()
        
        # --- BLOK 1: SMURF (8 trials + 2 buffer) ---
        self.run_block(1, self.trials_list_block1, self.smurf_agent)
        
        # Overgang til Blok 2
        self.trial_num = 0 # Nulstil tælleren for blok 2's data
        self.questionnaire_block(1)
        self._block_transition(1)

        # --- BLOK 2: SELF AGENT (8 trials + 2 buffer) ---
        self.run_block(2, self.trials_list_block2, self.self_agent)
        self.questionnaire_block(2)

        # Gem data
        self.save_data()
        
        # Afslut
        self.quit_experiment()

    def save_data(self):
        """Gemmer data i mappen 'Data' med Subject ID som filnavn."""
        
        # Filnavn er Subject ID + .csv
        filename = f'{self.subject_id}.csv'
        # Sti er Data/SubjectID.csv
        data_dir = 'Data'
        full_path = os.path.join(data_dir, filename)
        
        if not os.path.exists(data_dir):
            os.makedirs(data_dir) # Opret 'Data' mappen hvis den ikke eksisterer
            
        thisExp = data.ExperimentHandler(name='EM2_Kovacs_Replication', dataFileName=full_path)
        
        # Bestem hvilke nøgler der skal bruges for at logge alle data
        keys = ['subject_id', 'subject_name', 'trial_num', 'trial_type', 'Agent_Type', 
                'is_buffer', 'Questionnaire_Response', 'Question_ID', 'Question_Text',
                'response', 'rt', 'Ball_present', 'Part_belief', 'Agent_belief', 'Condition']
                
        for trial in self.trial_data:
            # Sikrer at Questionnaire-data og Trial-data kan logges i samme fil
            for key in keys:
                # Brug .get() for at få værdien, eller 'N/A' hvis nøglen ikke findes (f.eks. Trial-felter i Questionnaire-rækker)
                value = trial.get(key, 'N/A')
                # For Condition, som kun findes i Trial-data
                if key == 'Condition':
                    thisExp.addData(key, trial.get(key, 'N/A')) 
                elif key == 'Question_Text':
                    thisExp.addData(key, value)
                else:
                    thisExp.addData(key, value)
            
            thisExp.nextEntry() 
        
        thisExp.close()
        
        print(f"Data gemt til: {full_path}")


    def quit_experiment(self):
        if self.win is not None:
            self.win.close()
        core.quit()

# Kør eksperimentet
if __name__ == '__main__':
    # Kontrollér om 'Assets' mappen eksisterer
    if not os.path.exists(VIDEO_DIR):
        print(f"FEJL: Mappen '{VIDEO_DIR}' blev ikke fundet. Opret mappen og placer videoerne/billederne der.")
        core.quit()

    experiment = EM2Experiment()
    experiment.run_experiment()