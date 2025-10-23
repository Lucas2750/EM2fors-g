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

class EM2Experiment:
    def __init__(self):
        # Initialiser Subject ID som None
        self.subject_id = None 

        # Indstil vindue og andre standardindstillinger
        # Vigtigt: Vinduet skal kun åbnes EFTER Subject ID er indsamlet (se run_experiment)
        self.win = None 
        
        self.clock = core.Clock()
        self.trial_data = []
        self.trial_num = 0
        self.num_trials_per_condition = 1  # 8 betingelser * 1 = 8 trials
        self.num_trials_per_block = 8
        self.num_blocks = 2 # Smurf + Self Agent
        self.num_practice_trials = 4 # 4 praksis trials

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

        # Opret den fulde liste over forsøg for HVER blok (2 blokke * 80 forsøg)
        self.trials_list_block1 = self._create_shuffled_trials_list()
        self.trials_list_block2 = self._create_shuffled_trials_list()
        
        # Stimuli initialiseres senere i run_experiment()
        self.smurf_agent = None
        self.self_agent = None
        self.current_agent_stim = None

    def get_subject_id(self):
        """Indsamler Subject ID ved hjælp af en dialogboks."""
        dlg = gui.DlgFromDict(dictionary={'Subject ID (Indtast 4 cifre)': '', 'Navn:': ''}, 
                              title='Eksperiment Information')
        
        if dlg.OK:
            self.subject_id = dlg.dictionary['Subject ID (Indtast 4 cifre)']
            self.subject_name = dlg.dictionary['Navn:']
            # Validering af 4 cifre
            if not (len(self.subject_id) == 4 and self.subject_id.isdigit()):
                print("FEJL: Subject ID skal være 4 cifre. Forsøger igen.")
                self.subject_id = self.get_subject_id() # Rekursivt kald
            
            return self.subject_id
        else:
            # Hvis brugeren trykker Annuller
            core.quit()
            sys.exit()

    def setup_visual_stimuli(self):
        """Opretter PsychoPy vinduet og stimuli efter ID er indsamlet."""
        if self.win is None:
            self.win = visual.Window([1280, 720], color='black', fullscr=True, monitor='testMonitor', units='pix') 
            
            # Opret agent billed stimuli
            # X-positioner: Starter langt ude til venstre (-1300), stopper ved -250
            self.smurf_agent = visual.ImageStim(self.win, image=os.path.join(VIDEO_DIR, 'smurf1.png'), 
                                                pos=[-1300, 0], size=(200, 200))
            self.self_agent = visual.ImageStim(self.win, image=os.path.join(VIDEO_DIR, 'selfAgent.png'), 
                                               pos=[-1300, 0], size=(200, 200))
            # Initialiser agenten der skal bruges i starten
            self.current_agent_stim = self.smurf_agent
            
            # NYT: Opret tekst-stimulus til at vise navnet
            # Position (Y = 100) er sat til at være over agenten (150x150, centeret ved Y=0)
            self.name_stim = visual.TextStim(self.win, text=self.subject_name, 
                                             color='white', pos=[-1200, 200], height=30)


    def _create_shuffled_trials_list(self):
        """Opretter en randomiseret liste af betingelser for en hel blok."""
        condition_values = [cond['condition'] for cond in self.conditions]
        trials_list = condition_values * self.num_trials_per_condition
        random.shuffle(trials_list)
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

    def goodbye_instructions(self):
        # Bruger nu self.win
        goodbye = visual.TextStim(self.win, text="Tusind tak for at deltage i vores eksperiment!\n" \
        "\nVi testede hvorvidt om agentens, altså smølfen eller AI-versionen af dig, kunne påvirke dine svar.\n" \
        "\nAltså om dens tro på om bolden var bag væggen eller ej kunne påvirke din reaktionstid.\n" \
        "\nEndnu engang tak for deltagelsen, du må gerne hente os.\n" \
        "\nTryk på ‘ESC’ for at lukke programmet og gemme din data.", 
        color='white', wrapWidth=1200, height=30)
        goodbye.draw()
        self.win.flip()
        event.waitKeys(keyList=['esc'])

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
           Korrekt syntaks for PsychoPy 2023.1.3: Sæt 'flipHoriz' attributten direkte.
        """
        
        # Start X pos. (uden for skærmen)
        x_start = -1300 
        # Slut X pos. (lidt til venstre for centrum)
        x_end = -250 

        # Funktion til lineær interpolation
        def lerp(start, end, t, t_start, t_end):
            if t < t_start or t > t_end:
                return None
            progress = (t - t_start) / (t_end - t_start)
            return start + progress * (end - start)

        # 1. Bevægelse ind (0.0s - 3.5s): Bevæger sig mod højre. FlipHoriz = False
        if current_time >= T_START_IN and current_time <= T_END_IN:
            # RETTET: Sæt attributten direkte
            agent_stim.flipHoriz = False 
            x = lerp(x_start, x_end, current_time, T_START_IN, T_END_IN)
            if x is not None:
                agent_stim.setPos([x, 0])
                return

        # 2. Bevægelse ud (12.0s - 15.0s): Bevæger sig mod venstre. FlipHoriz = True
        elif current_time >= T_START_OUT and current_time <= T_END_OUT:
            # RETTET: Sæt attributten direkte
            agent_stim.flipHoriz = True 
            x = lerp(x_end, x_start, current_time, T_START_OUT, T_END_OUT)
            if x is not None:
                agent_stim.setPos([x, 0])
                return

        # 3. Bevægelse ind (18.0s - 21.0s): Bevæger sig mod højre igen. FlipHoriz = False
        elif current_time >= T_START_IN_2 and current_time <= T_END_IN_2:
            # RETTET: Sæt attributten direkte
            agent_stim.flipHoriz = False 
            x = lerp(x_start, x_end, current_time, T_START_IN_2, T_END_IN_2)
            if x is not None:
                agent_stim.setPos([x, 0])
                return

        # --- Fikserede positioner mellem bevægelser ---
        
        # Stoppet position (3.5s - 12.0s): Kigger mod højre. FlipHoriz = False
        elif current_time > T_END_IN and current_time < T_START_OUT:
            agent_stim.flipHoriz = False # RETTET
            agent_stim.setPos([x_end, 0])
            
        # Uden for skærmen (15.0s - 18.0s)
        elif current_time >= T_END_OUT and current_time < T_START_IN_2:
            agent_stim.setPos([x_start, 0])
            
        # Stoppet position (21.0s - 25.0s): Kigger mod højre. FlipHoriz = False
        elif current_time > T_END_IN_2 and current_time <= VIDEO_LENGTH:
            agent_stim.flipHoriz = False # RETTET
            agent_stim.setPos([x_end, 0])
            
        # Uden for skærmen (Før start)
        else:
             agent_stim.setPos([x_start, 0])

    def run_trial(self, condition_name, practice=False):
        # RETTET: Trial tælleren inkrementeres KUN én gang for hvert kald
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
                                    'Agent_Type': 'Smurf' if self.current_agent_stim == self.smurf_agent else 'Self'})
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
                
                # NYT: Håndter Navne-stimulus (Kun hvis Self-Agent er aktiv)
                if self.current_agent_stim == self.self_agent:
                    self.name_stim.setPos([agent_x, 100]) # Sæt navnet over agenten
                    self.name_stim.draw()
                
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
        # Sikkerhedscheck for ikke-besvaret forsøg (bør være fanget af timeout i løkken)
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
            'Agent_Type': 'Smurf' if self.current_agent_stim == self.smurf_agent else 'Self'
        })
        
        # Slet alle eventuelle resterende events fra bufferen
        event.clearEvents()
        
        # Fikseringskors (ITI)
        fixation = visual.TextStim(self.win, text='+', color='white', height=50)
        fixation.draw()
        self.win.flip()
        core.wait(2.0) 
 
        # RETTET: HELE DEN DUPLIKEREDE KODE FRA DIN FIL ER FJERNET HERFRA
        # Den duplikerede kode startede igen med 'self.trial_num += 1'
        # og kørte et nyt forsøg, hvilket gav dobbelt antal trials.

    def practice_trials(self):
        # ... (Praksis forsøg som før)
        practice_list = [cond['condition'] for cond in self.conditions] * (self.num_practice_trials // len(self.conditions))
        random.shuffle(practice_list)
        
        for condition_name in practice_list:
            # I praksis bruges Smurfen som standard
            self.current_agent_stim = self.smurf_agent
            self.run_trial(condition_name, practice=True)
            
        self.trial_num = 0
        self.trial_data = [] # Fjern praksis data
        
        end_practice_text = visual.TextStim(self.win, text="Du har nu gennemført prøveforsøgene." \
        "\nTryk på ‘SPACE’ for at starte hovedeksperimentet.", color='white', wrapWidth=700)
        end_practice_text.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])
        
    def _block_transition(self, block_num):
        """Viser en pausebesked mellem blokkene."""
        agent_type = "Smurf" if block_num == 1 else "Self-Agent (Eget billede)"
        
        transition_text = visual.TextStim(self.win, text=f"Blok {block_num} er færdig." \
        f"\nI næste blok skal du observere en ny Agent: {agent_type}." \
        "\nTag en kort pause.\n\nTryk på ‘SPACE’ når du er klar, for at fortsætte.", color='white', wrapWidth=700)
        transition_text.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])


    def run_block(self, block_num, trials_list, agent_stim):
        """Kører en hel eksperimentblok."""
        self.current_agent_stim = agent_stim
        
        for condition_name in trials_list:
            self.run_trial(condition_name, practice=False)

    def run_experiment(self):
        # 1. INDSAMLE SUBJECT ID FØR VINDUE ÅBNES
        self.get_subject_id()
        
        # 2. OPSÆT VINDUE OG STIMULI
        self.setup_visual_stimuli()
        
        # 3. KØR EKSPERIMENT
        
        # Vis instruktioner
        self.show_instructions()
        
        # Kør praksis (bruger Smurf Agent)
        self.practice_instructions()
        self.practice_trials()
        
        # --- BLOK 1: SMURF ---
        self.run_block(1, self.trials_list_block1, self.smurf_agent)
        
        # Overgang til Blok 2
        self.trial_num = 0 # Nulstil tælleren for blok 2's data
        self._block_transition(2)

        # --- BLOK 2: SELF AGENT ---
        self.run_block(2, self.trials_list_block2, self.self_agent)
            
        # Afsluttende instruktioner
        self.goodbye_instructions()

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
        
        for trial in self.trial_data:
            thisExp.addData('subject_id', self.subject_id) # Tilføj ID til hver række
            thisExp.addData('trial_num', trial['trial_num'])
            thisExp.addData('trial_type', trial['trial_type'])
            thisExp.addData('rt', trial['rt'])
            thisExp.addData('response', trial['response'])
            thisExp.addData('Ball_present', trial['Ball_present'])
            thisExp.addData('Part_belief', trial['Part_belief'])
            thisExp.addData('Agent_belief', trial['Agent_belief'])
            thisExp.addData('Correct', trial['Ball_present'] and trial['response'] == 'space' or not trial['Ball_present'] and trial['response'] == 'none')
            thisExp.addData('Agent_Type', trial['Agent_Type'])
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