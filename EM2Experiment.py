from psychopy import visual, core, event, data, gui
import random
import os
import sys # Til at afslutte programmet pænt ved annullering af dialog

# VERSION 0.8.9 (Rettet Skip-funktionalitet - Bruger 'p' i stedet for '+')

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
        self.smurf_name_stim = None 

    def get_subject_id(self):
        """Indsamler Subject ID og Navn ved hjælp af en dialogboks."""
        dlg = gui.DlgFromDict(dictionary={'Subject ID (Indtast 4 cifre)': '', 'Dit navn:': ''}, 
                              title='Eksperiment Information')
        
        if dlg.OK:
            self.subject_id = dlg.dictionary['Subject ID (Indtast 4 cifre)']
            self.subject_name = dlg.dictionary['Dit navn:']
            
            if not (len(self.subject_id) == 4 and self.subject_id.isdigit()):
                print("FEJL: Subject ID skal være 4 cifre. Forsøger igen.")
                self.subject_id = self.get_subject_id() 
            
            return self.subject_id
        else:
            core.quit()
            sys.exit()

    def setup_visual_stimuli(self):
        """Opretter PsychoPy vinduet og stimuli efter ID er indsamlet."""
        if self.win is None:
            self.win = visual.Window([1280, 720], color='black', fullscr=True, monitor='testMonitor', units='pix') 
            
            agent_size = (200, 200)
            self.smurf_agent = visual.ImageStim(self.win, image=os.path.join(VIDEO_DIR, 'smurf1.png'), 
                                                pos=[-1300, 0], size=agent_size)
            self.self_agent = visual.ImageStim(self.win, image=os.path.join(VIDEO_DIR, 'selfAgent.png'), 
                                               pos=[-1300, 0], size=agent_size)
            self.current_agent_stim = self.smurf_agent

            if self.subject_name is None:
                self.subject_name = "Navn" 
            
            self.name_stim = visual.TextStim(self.win, text=self.subject_name, 
                                             color='white', pos=[-1300, 150], height=30)
            
            self.smurf_name_stim = visual.TextStim(self.win, text="SMØLF", 
                                                   color='white', pos=[-1300, 150], height=30)


    def _create_shuffled_trials_list(self, include_buffer=False):
        """Opretter en randomiseret liste af betingelser for en hel blok, inkl. buffer-trials."""
        condition_values = [cond['condition'] for cond in self.conditions]
        
        trials_list = condition_values * self.num_trials_per_condition
        random.shuffle(trials_list)
        
        if include_buffer:
            buffer_trials = random.choices(condition_values, k=NUM_BUFFER_TRIALS)
            trials_list = buffer_trials + trials_list
            
        return trials_list

    def show_instructions(self):
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
        x_start = -1300 
        x_end = -250 
        current_x = x_start 

        def lerp(start, end, t, t_start, t_end):
            if t < t_start or t > t_end:
                return None
            progress = (t - t_start) / (t_end - t_start)
            return start + progress * (end - start)

        if current_time >= T_START_IN and current_time <= T_END_IN:
            agent_stim.flipHoriz = False 
            current_x = lerp(x_start, x_end, current_time, T_START_IN, T_END_IN)
            if current_x is not None:
                agent_stim.setPos([current_x, 0])
        elif current_time >= T_START_OUT and current_time <= T_END_OUT:
            agent_stim.flipHoriz = True 
            current_x = lerp(x_end, x_start, current_time, T_START_OUT, T_END_OUT)
            if current_x is not None:
                agent_stim.setPos([current_x, 0])
        elif current_time >= T_START_IN_2 and current_time <= T_END_IN_2:
            agent_stim.flipHoriz = False 
            current_x = lerp(x_start, x_end, current_time, T_START_IN_2, T_END_IN_2)
            if current_x is not None:
                agent_stim.setPos([current_x, 0])
        elif current_time > T_END_IN and current_time < T_START_OUT:
            agent_stim.flipHoriz = False 
            current_x = x_end
            agent_stim.setPos([current_x, 0])
        elif current_time >= T_END_OUT and current_time < T_START_IN_2:
            current_x = x_start
            agent_stim.setPos([current_x, 0])
        elif current_time > T_END_IN_2 and current_time <= VIDEO_LENGTH:
            agent_stim.flipHoriz = False 
            current_x = x_end
            agent_stim.setPos([current_x, 0])
        else:
             current_x = x_start
             agent_stim.setPos([current_x, 0])

        return current_x 

    def run_trial(self, condition_name, practice=False, is_buffer=False):
        self.trial_num += 1
        condition_details = self._get_condition_details(condition_name)
        if not condition_details:
             print(f"Betingelse {condition_name} blev ikke fundet. Springer over.")
             return False 

        trial_type = condition_name
        ball_is_present = condition_details['Ball_present']
        
        video_file = os.path.join(VIDEO_DIR, f'{condition_name}.mp4')
        
        if not os.path.exists(video_file):
            print(f"FEJL: Videofil '{video_file}' blev ikke fundet. Springer forsøg over.")
            error_stim = visual.TextStim(self.win, text=f"Fejl: Mangler {video_file}", color='red')
            error_stim.draw()
            self.win.flip()
            core.wait(2)
            self.trial_data.append({'trial_num': self.trial_num, 'trial_type': trial_type, 'response': 'FILE_MISSING', 'ReactionTime': -1, 
                                    'Ball_present': ball_is_present, 'Part_belief': condition_details['Part_belief'],
                                    'Agent_belief': condition_details['agent_belief'], 'Condition': condition_details['condition'],
                                    'Agent_Type': 'Smurf' if self.current_agent_stim == self.smurf_agent else 'Self',
                                    'is_buffer': is_buffer}) 
            return False 

        stimulus = visual.MovieStim3(self.win, filename=video_file, size=(1280, 720), loop=False) 
        
        event.clearEvents()
        
        responded = False
        response_start_time = 0.0
        response = 'None'
        ReactionTime = -1.0
        
        self.clock.reset()
        
        while self.clock.getTime() <= VIDEO_LENGTH and stimulus.status != visual.FINISHED:
            current_time = self.clock.getTime()
            
            # **RETTET:** Bruger 'p' som skip-tast
            keys = event.getKeys(keyList=['space', 'escape', 'p']) 
            
            if keys:
                if 'p' in keys: # HVIS 'p' trykkes: signalér skip
                    response = 'SKIP_BLOCK'
                    break
                elif 'escape' in keys:
                    self.quit_experiment()
                elif 'space' in keys and current_time >= RESPONSE_START_TIME and not responded:
                    responded = True
                    response = 'space'
                    ReactionTime = current_time - RESPONSE_START_TIME
                    break 

            
            # 1. Tegn videoen og agenten 
            stimulus.draw()
            if current_time is not None:
                agent_x = self._animate_agent(current_time, self.current_agent_stim)
                self.current_agent_stim.draw()
                
                if self.current_agent_stim == self.self_agent:
                    self.name_stim.setPos([agent_x, 150]) 
                    self.name_stim.draw()
                else: 
                    self.smurf_name_stim.setPos([agent_x, 150]) 
                    self.smurf_name_stim.draw()
                
            # 2. Håndtering af Timeouts (Starter ved 22.5s)
            if current_time >= RESPONSE_START_TIME and response_start_time == 0.0:
                 response_start_time = current_time 
            
            if current_time >= (RESPONSE_START_TIME + RESPONSE_DURATION) and not responded:
                 responded = True
                 ReactionTime = RESPONSE_DURATION 
                 response = 'no_press' if not ball_is_present else 'missed'
                 break 
            
            self.win.flip()
            
        if stimulus.status != visual.FINISHED:
            stimulus.stop()

        # --- Log trial data (kun hvis forsøget IKKE blev skippet) ---
        if response != 'SKIP_BLOCK':
            if not responded:
                ReactionTime = RESPONSE_DURATION
                response = 'no_press' if not ball_is_present else 'missed'

            self.trial_data.append({
                'trial_num': self.trial_num,
                'trial_type': trial_type,
                'response': response,
                'ReactionTime': ReactionTime,
                'Ball_present': condition_details['Ball_present'],
                'Part_belief': condition_details['Part_belief'],
                'Agent_belief': condition_details['agent_belief'],
                'Condition': condition_details['condition'],
                'Agent_Type': 'Smurf' if self.current_agent_stim == self.smurf_agent else 'Self',
                'is_buffer': is_buffer 
            })
        
            event.clearEvents()
            
            # Fikseringskors (ITI)
            fixation = visual.TextStim(self.win, text='+', color='white', height=50)
            fixation.draw()
            self.win.flip()
            core.wait(1.0) 

        # Returnerer status for at lade run_block vide, om den skal springe resten over
        return response == 'SKIP_BLOCK'

    def practice_trials(self):
        practice_list = [cond['condition'] for cond in self.conditions] * (self.num_practice_trials // len(self.conditions))
        random.shuffle(practice_list)
        
        for condition_name in practice_list:
            self.current_agent_stim = self.smurf_agent
            self.run_trial(condition_name, practice=True, is_buffer=False)
            
        self.trial_num = 0
        self.trial_data = [] # Fjern praksis data
        
        end_practice_text = visual.TextStim(self.win, text="Du har nu gennemført prøveforsøgene." \
        "\nTryk på ‘SPACE’ for at starte hovedeksperimentet.", color='white', wrapWidth=1200, height=30)
        end_practice_text.draw()
        self.win.flip()
        
        # **RETTET:** Tjek for skip practice her
        keys = event.waitKeys(keyList=['space', 'p', 'escape'])
        if 'p' in keys:
             print("Praksis forsøg sprunget over med 'p' tasten.")
             return 
        elif 'escape' in keys:
             self.quit_experiment()
        
    def _block_transition(self, block_num):
        """Viser en pausebesked mellem blokkene."""
        agent_type = f"Self-Agent ({self.subject_name})" 
        
        transition_text = visual.TextStim(self.win, text=f"Forbered dig på BLOK 2." \
        f"\nI denne blok skal du observere: {agent_type}." \
        "\nTag en kort pause.\n\nTryk på ‘SPACE’ for at fortsætte.", color='white', wrapWidth=1200, height=30)
        transition_text.draw()
        self.win.flip()
        
        # **RETTET:** Tjek for skip block tast (p)
        keys = event.waitKeys(keyList=['space', 'p', 'escape'])
        if 'p' in keys:
            print("Blok 2 overgang sprunget over af brugeren med 'p' tasten.")
            raise StopIteration("Blok 2 overgang sprunget over.")
        elif 'escape' in keys:
            self.quit_experiment()
    
    def run_block(self, block_num, trials_list, agent_stim):
        """Kører en hel eksperimentblok. Kan springes over med 'p'-tasten."""
        self.current_agent_stim = agent_stim
        
        for i, condition_name in enumerate(trials_list):
            
            is_buffer_trial = i < NUM_BUFFER_TRIALS
            
            # run_trial returnerer True hvis 'p' blev trykket (SKIP_BLOCK)
            skip_block = self.run_trial(condition_name, practice=False, is_buffer=is_buffer_trial)

            if skip_block:
                print(f"Blok {block_num} sprunget over af brugeren med 'p' tasten.")
                self.trial_num = 0
                return # Afslut run_block funktionen tidligt

    def log_skipped_questionnaire(self, agent_type):
        """Logs 'SKIPPED' for alle questionnaire items og rydder op i delvise svar."""
        
        num_questions_logged = 0
        for i in range(len(self.trial_data) - 1, -1, -1):
            if self.trial_data[i].get('trial_type') == 'Questionnaire' and self.trial_data[i].get('Agent_Type') == agent_type:
                num_questions_logged += 1
            else:
                break
        
        if num_questions_logged > 0:
            self.trial_data = self.trial_data[:-num_questions_logged]
            
        self.trial_num = 0 
        
        for q_idx, question_text in enumerate(self.questionnaire_questions):
            self.trial_num += 1 
            self.trial_data.append({
                'trial_num': self.trial_num,
                'trial_type': 'Questionnaire',
                'Agent_Type': agent_type,
                'Question_ID': q_idx + 1,
                'Question_Text': question_text,
                'Questionnaire_Response': 'SKIPPED',
                'is_buffer': 'N/A', 
                'response': 'N/A',
                'ReactionTime': 'N/A',
                'Ball_present': 'N/A',
                'Part_belief': 'N/A',
                'Agent_belief': 'N/A',
                'Condition': 'N/A'
            })

    def questionnaire_block(self, block_num):
        """Kører spørgeskemaet og logger svarene. Kan springes over med 'p'-tasten."""
        
        agent_type = "Smurf" if block_num == 1 else "Self"
        
        # Instruktioner
        instructions = visual.TextStim(self.win, text=
                                        "Du skal nu svare på en række udsagn, der relaterer sig til den blok, du lige har gennemført.\n" \
                                        "\nDu bliver præsenteret for et udsagn og skal derefter angive" \
                                        "\nhvor enig du er i det givne udsagn på en skala fra 1-7.\n" \
                                        "\n**1 = helt uenig og 7 = helt enig**"
                                        "\n\nTryk på ‘SPACE’ for at komme videre.", 
        color='white', wrapWidth=1200, height=30)
        instructions.draw()
        self.win.flip()
        
        # **RETTET:** Tjek for skip questionnaire tast (p) på instruktionsskærmen
        keys_inst = event.waitKeys(keyList=['space', 'p', 'escape'])
        if 'p' in keys_inst:
            print(f"Spørgeskema Blok {block_num} sprunget over af brugeren med 'p' tasten fra instruktionsskærmen.")
            self.log_skipped_questionnaire(agent_type)
            return
        elif 'escape' in keys_inst:
            self.quit_experiment()


        # Skala tekst (vises på alle spørgsmål)
        scale_text = visual.TextStim(self.win, text="**1 = Helt uenig** **7 = Helt enig**", 
                                     pos=[0, -300], height=25, color='gray')
        
        # Input/feedback tekst (RET FRA '+' til 'p')
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
                # Opdater prompten for at inkludere 'p' som skip
                response_text_stim.setText(f"Svar (1-7) eller Esc/p: {response_str}") 
                response_text_stim.draw()
                self.win.flip()
                
                # 2. Hent taster - TILFØJET 'p'
                keys = event.getKeys(keyList=['1', '2', '3', '4', '5', '6', '7', 'return', 'backspace', 'escape', 'p'])
                
                if keys:
                    key = keys[0]
                    
                    if key == 'p': # RET FRA '+'
                        print(f"Spørgeskema Blok {block_num} sprunget over af brugeren med 'p' tasten midt i spørgsmålene.")
                        self.log_skipped_questionnaire(agent_type)
                        return # Afslut questionnaire_block

                    if key in ['1', '2', '3', '4', '5', '6', '7']:
                        if len(response_str) == 0:
                            response_str = key
                    
                    elif key == 'backspace':
                        response_str = "" 
                        
                    elif key == 'return':
                        if response_str in ['1', '2', '3', '4', '5', '6', '7']:
                            valid_response = True
                            
                            self.trial_data.append({
                                'trial_num': self.trial_num,
                                'trial_type': 'Questionnaire',
                                'Agent_Type': agent_type,
                                'Question_ID': q_idx + 1,
                                'Question_Text': question_text,
                                'Questionnaire_Response': int(response_str),
                                'is_buffer': 'N/A', 
                                'response': 'N/A',
                                'ReactionTime': 'N/A',
                                'Ball_present': 'N/A',
                                'Part_belief': 'N/A',
                                'Agent_belief': 'N/A',
                                'Condition': 'N/A'
                            })
                            self.trial_num += 1 
                        else:
                            response_str = ""
                            
                    elif key == 'escape':
                        self.quit_experiment()
                        
            core.wait(0.5)
        
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
        
        self.show_instructions()
        
        # Kør praksis (bruger Smurf Agent)
        self.practice_instructions()
        self.practice_trials() 
        
        # --- BLOK 1: SMURF (8 trials + 2 buffer) ---
        self.run_block(1, self.trials_list_block1, self.smurf_agent)
        
        # Spørgeskema 1
        self.trial_num = 0 
        self.questionnaire_block(1)
        
        # Overgang til Blok 2
        self.trial_num = 0 
        try:
            self._block_transition(1) 
        except StopIteration:
            # Hvis vi springer over overgangen (og dermed Blok 2), skal vi logge data og afslutte
            self.save_data()
            self.quit_experiment()
            return

        # --- BLOK 2: SELF AGENT (8 trials + 2 buffer) ---
        self.run_block(2, self.trials_list_block2, self.self_agent) 
        self.questionnaire_block(2)

        # Gem data
        self.save_data()
        
        # Afslut
        self.quit_experiment()

    def save_data(self):
        """Gemmer data i mappen 'Data' med Subject ID som filnavn."""
        
        filename = f'{self.subject_id}.csv'
        data_dir = 'Data'
        full_path = os.path.join(data_dir, filename)
        
        if not os.path.exists(data_dir):
            os.makedirs(data_dir) 
            
        thisExp = data.ExperimentHandler(name='EM2_Kovacs_Replication', dataFileName=full_path)
        
        keys = ['subject_id', 'subject_name', 'trial_num', 'trial_type', 'Agent_Type', 
                'is_buffer', 'Questionnaire_Response', 'Question_ID', 'Question_Text',
                'response', 'ReactionTime', 'Ball_present', 'Part_belief', 'Agent_belief', 'Condition']
                
        for trial in self.trial_data:
            for key in keys:
                if key == 'subject_id':
                    value = self.subject_id
                elif key == 'subject_name':
                    value = self.subject_name
                else:
                    value = trial.get(key, 'N/A' )
                
                if key == 'Condition' and trial.get('trial_type') != 'Questionnaire' and isinstance(value, str) and len(value) > 4:
                    # Udfør beskæring: 'P+A+(+)' bliver til 'P+A-'
                    value = value[:4]
                
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
    if not os.path.exists(VIDEO_DIR):
        print(f"FEJL: Mappen '{VIDEO_DIR}' blev ikke fundet. Opret mappen og placer videoerne/billederne der.")
        core.quit()

    experiment = EM2Experiment()
    experiment.run_experiment()