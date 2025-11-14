from psychopy import visual, core, event, data, gui
import random
import os
import sys 
import csv 

# VERSION 0.9.7 (Rettet Agent Animation - Linear Interpolation FIX)

# Definer stien til videos
VIDEO_DIR = 'Assets'
# Tider for agent-animation (baseret på din 20 sek. video)
T_START_IN = 0.0
T_END_IN = 1.5
T_START_OUT = 9.5
T_END_OUT = 11.0
T_START_IN_2 = 13.0
T_END_IN_2 = 14.5
VIDEO_LENGTH = 18.0

# Tidspunkt for væggen fjernes/responsen skal starte (ca. 15.5s)
RESPONSE_START_TIME = 16.04
RESPONSE_DURATION = 1.9 # Responsvindue er 1.9 sekunder

# KONSTANT
NUM_BUFFER_TRIALS = 2 # Antal buffer forsøg i starten af hver blok

class EM2Experiment:
    def __init__(self):
        self.subject_id = None 
        self.subject_name = None 

        self.win = None 
        
        self.clock = core.Clock()
        self.trial_data = [] # Data gemmes midlertidigt her
        
        self.current_trial_counter = 0 
        self.num_trials_per_condition = 1  
        self.num_trials_per_block = 8 # 8 main trials
        self.num_blocks = 2 
        self.num_practice_trials = 8 

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
        
        # Opret den fulde liste over forsøg (2 buffer + 8 trials = 10 total)
        self.trials_list_block1 = self._create_shuffled_trials_list(include_buffer=True)
        self.trials_list_block2 = self._create_shuffled_trials_list(include_buffer=True)
        
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
                return self.get_subject_id() 
            
            return self.subject_id
        else:
            core.quit()
            sys.exit()

    def setup_visual_stimuli(self):
        """Opretter PsychoPy vinduet og stimuli."""
        if self.win is None:
            self.win = visual.Window([1920, 1080], color='black', fullscr=True, monitor='testMonitor', units='pix') 
            
            agent_size = (350, 700)
            self.smurf_agent = visual.ImageStim(self.win, image=os.path.join(VIDEO_DIR, 'smurf1.png'), 
                                                pos=[-2000, -200], size=agent_size)
            self.self_agent = visual.ImageStim(self.win, image=os.path.join(VIDEO_DIR, 'selfAgent.png'), 
                                               pos=[-2000, -200], size=agent_size)
            self.current_agent_stim = self.smurf_agent

            if self.subject_name is None:
                self.subject_name = "Navn" 
            
            self.name_stim = visual.TextStim(self.win, text=self.subject_name, 
                                             color='white', pos=[-2000, 500], height=30)
            
            self.smurf_name_stim = visual.TextStim(self.win, text="SMØLF", 
                                                   color='white', pos=[-2000, 500], height=30)


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
        """Viser introduktionsinstruktionerne."""
        instructions = visual.TextStim(self.win, text="Velkommen til vores eksperiment!\n" \
        "\nDu vil blive vist en video af en bold der bevæger sig." \
        "\nDit job er at i slutningen af videoen skal du svare på om bolden er bag en væg.\n" \
        "\nTryk IKKE på noget hvis bolden IKKE er bag væggen, når væggen fjernes." \
        "\nTryk på 'SPACE/Mellemrum' når du ser bolden bag væggen, når væggen fjernes.\n" \
        "\nDu skal først svare på dette, når væggen er væk! Dette er vigtigt, så du skal sidde klar.\n" \
        "\nDet er tilfældigt om bolden er bag væggen eller ej." \
        "\nSvar så hurtigt og præcist som muligt.\n" \
        "\nTryk på ‘SPACE’ for at starte.", 
        color='white', wrapWidth=1900, height=30)
        instructions.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])

    def practice_instructions(self):
        """Viser instruktioner for prøveforsøg."""
        practice_text = visual.TextStim(self.win, text="Nu vil du starte med nogle prøve forsøg." \
        "\nDisse vil hjælpe dig med at forstå opgaven bedre.\n" \
        "\nTryk på ‘SPACE’ for at starte.", color='white', wrapWidth=1900, height=30)
        practice_text.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])
    
    def _get_condition_details(self, condition_name):
        """Finder detaljerne for en betingelse."""
        for cond in self.conditions:
            if cond['condition'] == condition_name:
                return cond
        return None

    def _animate_agent(self, current_time, agent_stim):
        """Håndterer agentens bevægelse på skærmen."""
        agent_y_coord = -150
        x_start = -2000 
        x_end = -400 
        current_x = x_start 

        # FIX: Korrekt implementering af Linear Interpolation (lerp)
        def lerp(start, end, t, t_start, t_end):
            if t < t_start or t > t_end:
                return None
            progress = (t - t_start) / (t_end - t_start)
            # KORREKT MATEMATIK: start + (progress * distance)
            return start + progress * (end - start) 

        # Agent animation logik (Bevægelse ind/ud/ind igen)
        if current_time >= T_START_IN and current_time <= T_END_IN:
            agent_stim.flipHoriz = False 
            current_x = lerp(x_start, x_end, current_time, T_START_IN, T_END_IN)
            if current_x is not None:
                agent_stim.setPos([current_x, agent_y_coord])
        elif current_time >= T_START_OUT and current_time <= T_END_OUT:
            agent_stim.flipHoriz = True 
            current_x = lerp(x_end, x_start, current_time, T_START_OUT, T_END_OUT)
            if current_x is not None:
                agent_stim.setPos([current_x, agent_y_coord])
        elif current_time >= T_START_IN_2 and current_time <= T_END_IN_2:
            agent_stim.flipHoriz = False 
            current_x = lerp(x_start, x_end, current_time, T_START_IN_2, T_END_IN_2)
            if current_x is not None:
                agent_stim.setPos([current_x, agent_y_coord])
        # Positioner i mellemtiderne (Hold agenten på X_END, når animationen er færdig)
        elif current_time > T_END_IN and current_time < T_START_OUT:
            agent_stim.flipHoriz = False 
            current_x = x_end
            agent_stim.setPos([current_x, agent_y_coord])
        elif current_time >= T_END_OUT and current_time < T_START_IN_2:
            current_x = x_start
            agent_stim.setPos([current_x, agent_y_coord])
        elif current_time > T_END_IN_2 and current_time <= VIDEO_LENGTH:
            agent_stim.flipHoriz = False 
            current_x = x_end
            agent_stim.setPos([current_x, agent_y_coord])
        else:
             current_x = x_start
             agent_stim.setPos([current_x, agent_y_coord])

        return current_x 

    def run_trial(self, condition_name, practice=False, is_buffer=False, log_trial_num=0):
        """Kører et enkelt video-forsøg og logger data."""
        
        condition_details = self._get_condition_details(condition_name)
        if not condition_details:
             print(f"Betingelse {condition_name} blev ikke fundet. Springer over.")
             return False 

        ball_is_present = condition_details['Ball_present']
        
        video_file = os.path.join(VIDEO_DIR, f'{condition_name}.mp4')
        
        if not os.path.exists(video_file):
            print(f"FEJL: Videofil '{video_file}' blev ikke fundet. Springer forsøg over.")
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
            
            keys = event.getKeys(keyList=['space', 'escape', 'p']) 
            
            if keys:
                if 'p' in keys: 
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
                
            # 2. Håndtering af Timeouts (Svarvindue fra 22.5s til 25.0s)
            if current_time >= RESPONSE_START_TIME and response_start_time == 0.0:
                 response_start_time = current_time 
            
            if current_time >= (RESPONSE_START_TIME + RESPONSE_DURATION) and not responded:
                 responded = True
                 ReactionTime = RESPONSE_DURATION 
                 response = 'no_press' if not ball_is_present else 'missed' # 'missed' if no press when ball IS present
                 break 
            
            self.win.flip()
            
        if stimulus.status != visual.FINISHED:
            stimulus.stop()

        # --- Log trial data (kun hvis forsøget IKKE blev skippet) ---
        if response != 'SKIP_BLOCK':
            if not responded:
                ReactionTime = RESPONSE_DURATION
                response = 'no_press' if not ball_is_present else 'missed'
            
            if not practice:
                # Tilføj data til den midlertidige liste
                self.trial_data.append({
                    'trial_num': log_trial_num, # 1-8 for Main, 0 for Buffer
                    'trial_type': 'VideoTrial', 
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

        return response == 'SKIP_BLOCK'

    def practice_trials(self):
        """Kører prøveforsøgene."""
        practice_list = [cond['condition'] for cond in self.conditions] * (self.num_practice_trials // len(self.conditions))
        random.shuffle(practice_list)
        
        for condition_name in practice_list:
            self.current_agent_stim = self.smurf_agent
            self.run_trial(condition_name, practice=True, is_buffer=False, log_trial_num=0) 
            
        # Fjern praksis data, hvis det blev logget ved en fejl
        self.trial_data = [d for d in self.trial_data if d.get('trial_type') == 'VideoTrial' and d.get('is_buffer') in [True, False]]
        
        end_practice_text = visual.TextStim(self.win, text="Du har nu gennemført prøveforsøgene." \
        "\nTryk på ‘SPACE’ for at starte hovedeksperimentet.", color='white', wrapWidth=1200, height=30)
        end_practice_text.draw()
        self.win.flip()
        
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
        
        keys = event.waitKeys(keyList=['space', 'p', 'escape'])
        if 'p' in keys:
            print("Blok 2 overgang sprunget over af brugeren med 'p' tasten.")
            raise StopIteration("Blok 2 overgang sprunget over.")
        elif 'escape' in keys:
            self.quit_experiment()
    
    def run_block(self, block_num, trials_list, agent_stim):
        """Kører en hel eksperimentblok."""
        self.current_agent_stim = agent_stim
        self.current_trial_counter = 0 # Nulstilles før hver blok for at tælle main trials (1 til 8)
        
        for i, condition_name in enumerate(trials_list):
            
            is_buffer_trial = i < NUM_BUFFER_TRIALS
            log_num = 0
            
            if not is_buffer_trial:
                self.current_trial_counter += 1
                log_num = self.current_trial_counter # 1 til 8
            
            skip_block = self.run_trial(condition_name, practice=False, 
                                        is_buffer=is_buffer_trial, log_trial_num=log_num)

            if skip_block:
                print(f"Blok {block_num} sprunget over af brugeren med 'p' tasten.")
                return 

    def show_goodbye_screen(self):
        """Viser afslutningsbeskeden."""
        goodbye_text = "Tak for at være med i vores forsøg! 🙏\n\n" \
                       "Du er nu færdig.\n" \
                       "Du kan nu gå ud til eksperimentatoren.\n\n" \
                       "Tryk på 'SPACE' for at afslutte."
        
        goodbye_stim = visual.TextStim(self.win, text=goodbye_text, 
                                       color='white', wrapWidth=1200, height=35)
        goodbye_stim.draw()
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
        
        # --- BLOK 1: SMURF (2 buffer + 8 main trials) ---
        self.run_block(1, self.trials_list_block1, self.smurf_agent)
        
        # Overgang til Blok 2
        try:
            self._block_transition(1) 
        except StopIteration:
            self.save_data()
            self.show_goodbye_screen() 
            self.quit_experiment()
            return

        # --- BLOK 2: SELF AGENT (2 buffer + 8 main trials) ---
        self.run_block(2, self.trials_list_block2, self.self_agent) 

        # Gem data i den ene fil
        self.save_data()
        
        self.show_goodbye_screen()
        self.quit_experiment()

    # Gemmer KUN Video Trials data manuelt med CSV-modulet
    def save_data(self):
        """Gemmer KUN Video Trials data manuelt med Python's CSV-modul for øget robusthed."""
        
        data_dir = 'Data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir) 

        # --- 1. Forberedelse af data (Streng Filtrering) ---
        # VIGTIGT: Filtrer KUN main trials (hvor trial_num er 1-8, IKKE 0 for buffer/praksis)
        video_trials_data = [d for d in self.trial_data if d.get('trial_num', 0) > 0 and d.get('trial_type') == 'VideoTrial']
        
        if not video_trials_data:
            print("ADVARSEL: video_trials_data er TOM. Ingen data blev gemt. Tjek om trials blev kørt korrekt (ikke kun buffer/praksis).")
            return
        
        # --- 2. Gem Video Trials data ---
        filename_video = f'{self.subject_id}_VideoTrials.csv'
        full_path_video = os.path.join(data_dir, filename_video)
        
        # Nøgler/kolonne-navne til Video Trials
        fieldnames_video = ['subject_id', 'subject_name', 'trial_num', 'Condition', 'Agent_Type', 
                            'response', 'ReactionTime', 'Ball_present', 'Part_belief', 'Agent_belief']
        
        # Forbered rækkerne (sikker adgang til ordbogsværdier)
        video_rows_to_write = []
        for trial in video_trials_data:
            # Beskær condition-navnet ('P+A+(+)' bliver til 'P+A+')
            condition_name = trial.get('Condition', 'N/A')
            if isinstance(condition_name, str):
                # KORREKT IMPLEMENTERING: Tager kun de første 4 tegn
                truncated_condition = condition_name[:4] 
            else:
                truncated_condition = condition_name
        for trial in video_trials_data:
            row = {
                'subject_id': self.subject_id,
                'subject_name': self.subject_name,
                'trial_num': trial.get('trial_num', 'N/A'),
                'Condition': truncated_condition,
                'Agent_Type': trial.get('Agent_Type', 'N/A'),
                'response': trial.get('response', 'N/A'),
                'ReactionTime': trial.get('ReactionTime', -1.0),
                'Ball_present': trial.get('Ball_present', 'N/A'),
                'Part_belief': trial.get('Part_belief', 'N/A'),
                'Agent_belief': trial.get('Agent_belief', 'N/A'),
            }
            
            # Beskær condition-navnet ('P+A+(+)' bliver til 'P+A+')
            condition_name = trial.get('Condition', 'N/A')
            if isinstance(condition_name, str):
                row['Condition'] = condition_name[:4] 
            else:
                row['Condition'] = condition_name
                
            video_rows_to_write.append(row)


        try:
            # Åbn filen til skrivning og brug csv.DictWriter
            with open(full_path_video, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames_video)
                writer.writeheader()
                writer.writerows(video_rows_to_write)
            print(f"Video data gemt til: {full_path_video}")
            print(f"Antal rækker gemt (Main Trials): {len(video_rows_to_write)}")
        except Exception as e:
            # Hvis der er en problem med stien eller tilladelser
            print(f"FATAL FEJL ved skrivning af video data: {e}")
            print("Kontroller venligst mappetilladelserne for 'Data'-mappen eller stien.")


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