from psychopy import visual, core, event, data, gui
import random
import os
import sys 
import csv 

# VERSION 1.0.2 (Opdaterede tider og fikset visning af agent navn/tekst)

# Definer stien til videos
VIDEO_DIR = 'FilmAssets' # Opdateret sti
# Tider for agent-animation (baseret på din 18 sek. video)
T_START_IN = 0.0
T_END_IN = 1.5 # Opdateret tid
T_START_OUT = 9.5 # Opdateret tid
T_END_OUT = 11.0
T_START_IN_2 = 13.0 # Opdateret tid
T_END_IN_2 = 14.5 # Opdateret tid
VIDEO_LENGTH = 18.0 # Opdateret tid

# Tidspunkt for væggen fjernes/responsen skal starte (ca. 16.0s)
RESPONSE_START_TIME = 16.0 # Opdateret tid
RESPONSE_DURATION = 2.0 # Opdateret tid

# KONSTANT
NUM_BUFFER_TRIALS = 2 # Antal buffer forsøg i starten af hver blok

# KONSTANTER FOR ATTENTION CHECK (X-TAST)
X_PRESS_WINDOW_START = T_START_OUT  # 9.5s: Agenten starter med at forlade skærmen
X_PRESS_WINDOW_END = T_START_IN_2   # 13.0s: Agenten starter med at komme tilbage

class EM2Experiment:
    def __init__(self):
        self.subject_id = None 
        self.subject_name = None 

        self.win = None 
        
        self.clock = core.Clock()
        self.trial_data = [] # Data gemmes midlertidigt her
        
        self.current_trial_counter = 0 
        self.num_trials_per_condition = 5  
        self.num_trials_per_block = 40 
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
            self.win = visual.Window(color='black', fullscr=True, monitor='testMonitor', units='pix') 
            
            agent_size = (400, 700)
            agent_y_coord = -150 
            x_start = -2000 # Off-screen position

            self.smurf_agent = visual.ImageStim(self.win, image=os.path.join(VIDEO_DIR, 'smurf1.PNG'), 
                                                pos=[x_start, agent_y_coord], size=agent_size)
            self.self_agent = visual.ImageStim(self.win, image=os.path.join(VIDEO_DIR, 'selfAgent.png'), 
                                               pos=[x_start, agent_y_coord], size=agent_size)
            self.current_agent_stim = self.smurf_agent

            if self.subject_name is None:
                self.subject_name = "Navn" 
            
            # Initialiseres off-screen
            self.name_stim = visual.TextStim(self.win, text=self.subject_name, 
                                             color='black', pos=[x_start, 100], height=50)
            
            self.smurf_name_stim = visual.TextStim(self.win, text="Smølf", 
                                                   color='black', pos=[x_start, 100], height=50)


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
        """Viser introduktionsinstruktionerne for hovedopgaven."""
        instructions = visual.TextStim(self.win, text="Velkommen til vores eksperiment!\n" \
        "\nDu vil blive vist en video af en bold der bevæger sig." \
        "\nDit job er at i slutningen af videoen skal du svare på om bolden er bag en væg.\n" \
        "\nTryk IKKE på noget hvis bolden IKKE er bag væggen, når væggen fjernes." \
        "\nTryk på 'B' når du ser bolden bag væggen, når væggen fjernes.\n" \
        "\nDu skal først svare på dette, når væggen er væk! Dette er vigtigt, så du skal sidde klar.\n" \
        "\nDet er tilfældigt om bolden er bag væggen eller ej." \
        "\nSvar så hurtigt og præcist som muligt.\n" \
        "\nTryk på ‘SPACE’ for at fortsætte til næste instruktionsside.", 
        color='white', wrapWidth=1900, height=30)
        instructions.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])
    
    def show_instructions2(self):
        """Viser instruktionerne for opmærksomhedstesten ('x'-tasten)."""
        instructions = visual.TextStim(self.win, text="For at sørge for at du fokuserer på opgaven, \n" \
        "så skal du trykke på 'X', når agenten er på vej ud af skærmen eller ude af af skærmen.\n\n" \
        "Dette vil give mere mening når du starter med prøve forsøgene.\n\n" \
        "Der er aller først prøve forsøgene, som vil give dig en forståelse for forsøget.\n" \
        "Så kommer der 2 blokke af 40 trials hver, i alt 80 trials.\n" \
        "Det hele vil tage omkring 30 minutter.\n" \
        "\nHusk 'X' når agenten er ude, og 'B' når du ser bolden, efter væggen er fjernet.\n\n" \
        "Tryk på 'SPACE' for at gå videre.",
        color='white', wrapWidth=1900, height=30)
        instructions.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])

    def practice_instructions(self):
        """Viser instruktioner for prøveforsøg."""
        practice_text = visual.TextStim(self.win, text="Nu vil du starte med nogle prøve trials." \
        "\nDisse vil hjælpe dig med at forstå opgaven bedre.\n" \
        "\nHusk: 'X' når agenten er ude, og 'B' når du ser bolden bag væggen.\n" \
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
        """
        Håndterer agentens bevægelse på skærmen.
        Bruger Clamped Lerp for at sikre smooth start og slut.
        """
        agent_y_coord = -150
        x_start = -2000 # Off-screen
        x_end = -400 # On-screen position
        current_x = x_start # Standard position

        # Funktion til lineær interpolation
        def lerp(start, end, t, t_start, t_end):
            if t < t_start or t > t_end:
                return None
            progress = (t - t_start) / (t_end - t_start)
            return start + progress * (end - start)

        # 1. Bevægelse ind (0.0s - 1.5s): Bevæger sig mod højre. FlipHoriz = False
        if current_time >= T_START_IN and current_time <= T_END_IN:
            agent_stim.flipHoriz = False 
            current_x = lerp(x_start, x_end, current_time, T_START_IN, T_END_IN)
            if current_x is not None:
                agent_stim.setPos([current_x, agent_y_coord])

        # 2. Bevægelse ud (12.0s - 15.0s): Bevæger sig mod venstre. FlipHoriz = True
        elif current_time >= T_START_OUT and current_time <= T_END_OUT:
            agent_stim.flipHoriz = True 
            current_x = lerp(x_end, x_start, current_time, T_START_OUT, T_END_OUT)
            if current_x is not None:
                agent_stim.setPos([current_x, agent_y_coord])

        # 3. Bevægelse ind (18.0s - 21.0s): Bevæger sig mod højre igen. FlipHoriz = False
        elif current_time >= T_START_IN_2 and current_time <= T_END_IN_2:
            agent_stim.flipHoriz = False 
            current_x = lerp(x_start, x_end, current_time, T_START_IN_2, T_END_IN_2)
            if current_x is not None:
                agent_stim.setPos([current_x, agent_y_coord])

        # --- Fikserede positioner mellem bevægelser ---

        # Stoppet position (3.5s - 12.0s): Kigger mod højre. FlipHoriz = False
        elif current_time > T_END_IN and current_time < T_START_OUT:
            agent_stim.flipHoriz = False 
            current_x = x_end
            agent_stim.setPos([current_x, agent_y_coord])

        # Uden for skærmen (15.0s - 18.0s)
        elif current_time >= T_END_OUT and current_time < T_START_IN_2:
            current_x = x_start
            agent_stim.setPos([current_x, agent_y_coord])

        # Stoppet position (21.0s - 25.0s): Kigger mod højre. FlipHoriz = False
        elif current_time > T_END_IN_2 and current_time <= VIDEO_LENGTH:
            agent_stim.flipHoriz = False 
            current_x = x_end
            agent_stim.setPos([current_x, agent_y_coord])

        # Uden for skærmen (Før start)
        else:
             current_x = x_start
             agent_stim.setPos([current_x, agent_y_coord])

        return current_x # Returner X-positionen

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

        stimulus = visual.MovieStim3(self.win, size=[1280,720], filename=video_file, loop=False) 
        
        event.clearEvents()
        
        # Hovedopgave (B-tast)
        responded = False
        response_start_time = 0.0
        response = 'None'
        ReactionTime = -1.0
        
        # Sekundær opgave (X-tast)
        x_hit = 'No'
        x_rt = -1.0
        x_false_alarm_count = 0
        
        self.clock.reset()
        
        while self.clock.getTime() <= VIDEO_LENGTH and stimulus.status != visual.FINISHED:
            current_time = self.clock.getTime()
            
            # KeyList inkluderer nu 'b' og 'x'
            keys = event.getKeys(keyList=['b', 'x', 'escape', 'p']) 
            
            if keys:
                if 'p' in keys: 
                    response = 'SKIP_BLOCK'
                    break
                elif 'escape' in keys:
                    self.quit_experiment()
                
                # --- HOVEDOPGAVE: B-Tast ---
                elif 'b' in keys and current_time >= RESPONSE_START_TIME and not responded:
                    responded = True
                    response = 'b_press' # Logger press
                    ReactionTime = current_time - RESPONSE_START_TIME
                    # Bryder IKKE loopet her, da vi skal fortsætte for at spore 'x' og lade videoen slutte

                # --- SEKUNDÆR OPGAVE: X-Tast ---
                elif 'x' in keys:
                    # Tjek om vi er i det korrekte vindue
                    if current_time >= X_PRESS_WINDOW_START and current_time <= X_PRESS_WINDOW_END:
                        if x_hit == 'No': # Log kun første korrekte tryk (Hit)
                            x_hit = 'Yes'
                            x_rt = current_time - X_PRESS_WINDOW_START
                    else:
                        # Hvis trykket er uden for vinduet, tæl det som False Alarm
                        x_false_alarm_count += 1


            
            # 1. Tegn videoen og agenten 
            stimulus.draw()
            if current_time is not None:
                agent_x = self._animate_agent(current_time, self.current_agent_stim)
                
                # NY FIKS: Vurder om agenten er synlig baseret på tid
                is_agent_visible = (current_time > T_START_IN and current_time < T_END_OUT) or \
                                   (current_time > T_START_IN_2 and current_time <= VIDEO_LENGTH)
                
                # Tegn KUN agenten og navnet, hvis den er synlig
                if is_agent_visible:
                    self.current_agent_stim.draw()
                    
                    if self.current_agent_stim == self.self_agent:
                        self.name_stim.setPos([agent_x, 250]) 
                        self.name_stim.draw()
                    else: 
                        self.smurf_name_stim.setPos([agent_x, 250]) 
                        self.smurf_name_stim.draw()
                
            # 2. Håndtering af Timeouts (Svarvindue for B-tast)
            if current_time >= RESPONSE_START_TIME and response_start_time == 0.0:
                 response_start_time = current_time 
            
            if current_time >= (RESPONSE_START_TIME + RESPONSE_DURATION) and not responded:
                 responded = True
                 ReactionTime = RESPONSE_DURATION 
                 response = 'no_press' if not ball_is_present else 'missed' # 'missed' if no press when ball IS present
                 # Bryder IKKE loopet her, da vi skal lade videoen slutte
            
            self.win.flip()
            
        if stimulus.status != visual.FINISHED:
            stimulus.stop()

        # --- Færdiggør hovedopgavens respons (hvis den ikke allerede blev brudt af 'p') ---
        if response != 'SKIP_BLOCK':
            
            # Sætter endelig respons-tekst for B-tast
            if not responded:
                ReactionTime = RESPONSE_DURATION
                response = 'no_press' if not ball_is_present else 'missed'
            elif response == 'b_press':
                if ball_is_present:
                     response = 'hit'
                else:
                     response = 'false_alarm'

            # -------------------------------------------------------------------
            # 1. FEEDBACK IMPLEMENTATION (KUN FOR PRACTICE TRIALS) 
            # -------------------------------------------------------------------
            feedback_text = ""
            if practice:
                # Logik for B-tast feedback
                if ball_is_present:
                    if response == 'hit':
                        feedback_text = "Rigtigt!" 
                    elif response == 'missed':
                        feedback_text = "Husk at trykke 'B' når du ser bolden"
                else: # Bold is not present
                    if response == 'no_press':
                        feedback_text = "Rigtigt!" 
                    elif response == 'false_alarm':
                        feedback_text = "Husk du skal ikke trykke 'B' hvis du ikke ser bolden"
                
                # Logik for X-tast feedback (tilføj til eksisterende feedback)
                x_feedback = ""
                if x_hit == 'No':
                    x_feedback = "\n\nOBS: Du missede at trykke 'X' da agenten var ude af skærmen."
                elif x_false_alarm_count > 0:
                    x_feedback = f"\n\nOBS: Du trykkede 'X' {x_false_alarm_count} gang(e) uden for vinduet. \nTryk kun når agenten er ude eller på vej ud."

                # Kombiner feedback
                if x_feedback:
                    feedback_text += x_feedback
                
                if feedback_text:
                    # Vis feedback og vent på at deltageren fortsætter
                    feedback_stim = visual.TextStim(self.win, text=feedback_text, 
                                                    color='white', wrapWidth=1200, height=40)
                    feedback_stim.draw()
                    self.win.flip()
                    core.wait(0.5) 
                    event.waitKeys(keyList=['space']) # Venter på Mellemrumstasten for at fortsætte
            # -------------------------------------------------------------------
            
            if not practice:
                # Tilføj data til den midlertidige liste (KUN for Hovedforsøg)
                self.trial_data.append({
                    'trial_num': log_trial_num, 
                    'trial_type': 'VideoTrial', 
                    'response': response, # hit/false_alarm/no_press/missed
                    'ReactionTime': ReactionTime,
                    'Ball_present': condition_details['Ball_present'],
                    'Part_belief': condition_details['Part_belief'],
                    'Agent_belief': condition_details['agent_belief'],
                    'Condition': condition_details['condition'],
                    'Agent_Type': 'Smurf' if self.current_agent_stim == self.smurf_agent else 'Self',
                    'is_buffer': is_buffer,
                    # NYE FELTER FOR OPMÆRKSOMHEDSOPGAVEN
                    'X_Hit': x_hit,
                    'X_RT': x_rt,
                    'X_FalseAlarm_Count': x_false_alarm_count 
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
            # run_trial kaldes med practice=True, hvilket aktiverer feedback
            self.run_trial(condition_name, practice=True, is_buffer=False, log_trial_num=0) 
            
        # Fjern praksis data, hvis det blev logget ved en fejl
        self.trial_data = [d for d in self.trial_data if d.get('trial_num', 0) > 0 and d.get('trial_type') == 'VideoTrial']
        
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
        agent_type = f"En smølf" 
        
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
        goodbye_text = "Tak for at være med i vores forsøg! \n\n" \
                       "Du er nu færdig og kan svare på spørgeskemaet\n" \
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
        self.show_instructions2() 
        
        # Kør praksis (bruger Smurf Agent)
        self.practice_instructions()
        self.practice_trials() 
        
        # --- BLOK 1: SMURF (2 buffer + 8 main trials) ---
        self.run_block(2, self.trials_list_block2, self.self_agent) 
        
        # Overgang til Blok 2
        try:
            self._block_transition(1) 
        except StopIteration:
            self.save_data()
            self.show_goodbye_screen() 
            self.quit_experiment()
            return

        # --- BLOK 2: SELF AGENT (2 buffer + 8 main trials) ---
        self.run_block(1, self.trials_list_block1, self.smurf_agent)

        # Gem data i den ene fil
        self.save_data()
        
        self.show_goodbye_screen()
        self.quit_experiment()

    # Gemmer KUN Video Trials data manuelt med CSV-modulet
    def save_data(self):
        """Gemmer KUN Video Trials data manuelt med Python's CSV-modul for øget robusthed."""
        
        data_dir = 'data'
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
                            'response', 'ReactionTime', 'Ball_present', 'Part_belief', 'Agent_belief',
                            'X_Hit', 'X_RT', 'X_FalseAlarm_Count']
        
        # Forbered rækkerne (sikker adgang til ordbogsværdier)
        video_rows_to_write = []
        for trial in video_trials_data:
            # Beskær condition-navnet ('P+A+(+)' bliver til 'P+A+')
            condition_name = trial.get('Condition', 'N/A')
            if isinstance(condition_name, str):
                truncated_condition = condition_name[:4] 
            else:
                truncated_condition = condition_name
                
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
                # FELTER FOR OPMÆRKSOMHEDSOPGAVEN
                'X_Hit': trial.get('X_Hit', 'N/A'),
                'X_RT': trial.get('X_RT', -1.0),
                'X_FalseAlarm_Count': trial.get('X_FalseAlarm_Count', 0),
            }
                
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