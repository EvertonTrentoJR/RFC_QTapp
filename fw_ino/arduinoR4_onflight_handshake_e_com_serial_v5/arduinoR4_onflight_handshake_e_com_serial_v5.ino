#define MOTOR_ON()    (R_PORT1->PORR = (1 << 6)) // PORR = Reset (Coloca em LOW/0)
#define MOTOR_OFF()   (R_PORT1->POSR = (1 << 6)) // POSR = Set   (Coloca em HIGH/1)


#define SET_DIR_CW()  (R_PORT1->POSR = (1 << 12)) // Coloca D3 em HIGH
#define SET_DIR_CCW() (R_PORT1->PORR = (1 << 12)) // Coloca D3 em LOW

// Inversão Segura: Lê o estado atual do registrador de saída e aplica a inversão
#define INV_DIR()     if(R_PORT1->PODR & (1 << 12)) { SET_DIR_CCW(); } else { SET_DIR_CW(); }


#define STEP_HIGH()   (R_PORT1->POSR = (1 << 4)) // Coloca D2 em HIGH
#define STEP_LOW()    (R_PORT1->PORR = (1 << 4)) // Coloca D2 em LOW
const int encSignal1 = 11;//
const int encSignal2 = 10;//
float ang_abs = 0;// valor para dar localização absoluta

void setup() {

  pinMode(encSignal1, INPUT);
  pinMode(encSignal2, INPUT);
  pinMode(2, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(4, OUTPUT);
  MOTOR_ON();
  delay(10); 
  SET_DIR_CW();
  delay(10);

  Serial.begin(2000000);
  delay(500);
}
void loop() {
  // Recebeu Alguma coisa da Serial?
  if (Serial.available() > 0) {
    char comando = Serial.read();

    // Recebeu o Home
    if (comando == 'h' || comando == 'H') {
      Serial.println(comando);
      unsigned long timeout = millis();
      bool confirmado = false;
      // Espera pela confirmação "OK"
      while (millis() - timeout < 5000) {
        if (Serial.available() > 0) {
          String resposta = Serial.readStringUntil('\n');
          resposta.trim(); // Remove espaços ou \r
          if (resposta.equalsIgnoreCase("OK")) {
            confirmado = true;
            break;
          }
        }
      }
      //Se recebeu o OK, executa. Se não, ignora e volta ao loop
      if (confirmado) {
        Homing();
      } else {}
    }

    // Recebeu o angle
    if (comando == 'a' || comando == 'A') {
      float deg = Serial.parseFloat();
      float v_max = Serial.parseFloat();
      float acc = Serial.parseFloat();
      // Envia o comando de volta para conferência
      Serial.print(comando);
      Serial.print(",");
      Serial.print(deg);
      Serial.print(",");
      Serial.print(v_max);
      Serial.print(",");
      Serial.println(acc);
      // Espera pela confirmação "OK"
      unsigned long timeout = millis();
      bool confirmado = false;
      while (millis() - timeout < 5000) {
        if (Serial.available() > 0) {
          String resposta = Serial.readStringUntil('\n');
          resposta.trim(); // Remove espaços ou \r
          if (resposta.equalsIgnoreCase("OK")) {
            confirmado = true;
            break;
          }
        }
      }
      //Se recebeu o OK, executa. Se não, ignora e volta ao loop
      if (confirmado) {
        mov_function(deg, v_max, acc);
      } else {}
    }

    // Recebeu o Continuous
    else if (comando == 'm' || comando == 'M') {
      float deg = Serial.parseFloat();
      float v_max = Serial.parseFloat();
      float acc = Serial.parseFloat();
      int rep = Serial.parseFloat();
      unsigned long stop_time = Serial.parseFloat();
      // Envia o comando de volta para conferência
      Serial.print(comando);
      Serial.print(",");
      Serial.print(deg);
      Serial.print(",");
      Serial.print(v_max);
      Serial.print(",");
      Serial.print(acc);
      Serial.print(",");
      Serial.print(rep);
      Serial.print(",");
      Serial.println(stop_time);
      // Espera pela confirmação "OK"
      unsigned long timeout = millis();
      bool confirmado = false;
      while (millis() - timeout < 5000) {
        if (Serial.available() > 0) {
          String resposta = Serial.readStringUntil('\n');
          resposta.trim(); // Remove espaços ou \r
          if (resposta.equalsIgnoreCase("OK")) {
            confirmado = true;
            break;
          }
        }
      }
      //Se recebeu o OK, executa. Se não, ignora e volta ao loop
      if (confirmado) {
        mov_function(-deg / 2.0, 2.0, 0.33);
        deg = -deg;
        for (int i = 0; rep == 0 || i < rep; i++) {
          deg = -deg;
          delay(stop_time);
          mov_function(deg, v_max, acc);
          deg = -deg;
          delay(stop_time);
          mov_function(deg, v_max, acc);
          // Parada por "x" na serial
          if (Serial.available() > 0) {
            char letra = Serial.read();
            if (letra == 'x' || letra == 'X') {
              deg = -deg;
              mov_function(deg / 2.0, 2.0, 0.33);
              
              Serial.println("X");
              break;
            }
          }
        }
      }
    }

    // Recebeu o Info
    else if (comando == 'i' || comando == 'I') {
      Serial.println(F("\n================================================"));
      Serial.println(F("              FUNCAO DE MOVIMENTO [M]           "));
      Serial.println(F("================================================"));
      Serial.println(F("Comando: M [GRAUS] [VEL_MAX] [Ka]          "));
      Serial.println(F("Exemplo: M 30 1 0.33                            "));
      Serial.println(F("------------------------------------------------"));
      Serial.println(F("> GRAUS:     360 (Deslocamento angular em graus)"));
      Serial.println(F("> VEL_MAX:     1 (Velociade maxima em RPM)      "));
      Serial.println(F("> Ka:  0.33 (fração do movimeto em aceleração)  "));
      Serial.println(F("================================================\n"));
      Serial.println(F("\n================================================"));
      Serial.println(F("                FUNCAO DE CICLO [C]             "));
      Serial.println(F("================================================"));
      Serial.println(F("Comando: C [GRAUS] [VEL_MAX] [Ka] [REPET] [STOP TIME] "));
      Serial.println(F("Exemplo: C 30 1 0.33 5 500                         "));
      Serial.println(F("------------------------------------------------"));
      Serial.println(F("> GRAUS:      30 (deslocamento angular em graus)"));
      Serial.println(F("> VEL_MAX:     1 (Velociade maxima em RPM)      "));
      Serial.println(F("> Ka:  0.33 (fração do movimeto em aceleração)"));
      Serial.println(F("> REPET:       5 (quantidade de ciclos) se for zero repeti infinitamente até o comando x         "));
      Serial.println(F("> STOPTIME:  500 (tempo entre movimentos em ms) "));
      Serial.println(F("------------------------------------------------"));
      Serial.println(F("Nota: O ciclo executara o movimento completo    "));
      Serial.println(F("repetindo-o pelo numero de vezes programado.    "));
      Serial.println(F("================================================\n"));

    }
  }
}


void Pulse() { // Função para dar um pulso (~20us).
  STEP_HIGH();
  delayMicroseconds(10);
  STEP_LOW();
  delayMicroseconds(10);
}


void mov_function(float degrees_f, float vel_max, float acel) { // Função para movimentar (calcula a rampa trapezoidal e executata ela).
  bool direction;

  if (degrees_f < 0) {
    degrees_f = -degrees_f;
    direction = 1;
    SET_DIR_CCW();
  } else {
    SET_DIR_CW();
    direction = 0;
  }
  vel_max = constrain(vel_max, 0.1, 20.0);
  acel = constrain(acel, 0.01, 0.5);
  degrees_f = constrain(degrees_f, 0.01, 360.0);
  delayMicroseconds(50);
  int pulses_rev = 25600 * 4; // x4 p  causa do redutor
  int Pulse_N = round((degrees_f * (float)pulses_rev) / 360.0); // Número de pulsos para ser dado
  int vel_max_int = (int)((567.0 / vel_max)); // velocidade maxima*(constante)
  float rampStep = Pulse_N * acel; // inclinação da aceleração
  int pulse_ramp = min((int)rampStep, Pulse_N / 2); //   Menor tamanho da função ser um triangulo
  // calculo para definir a velocidade maxima segura
  if (vel_max_int * pulse_ramp <= 20000) {
    vel_max_int = (int)(20000 / pulse_ramp);
    Serial.print("Aceleração crítica alcançada, Velociade máxima definida para:");
    Serial.println(567.0 / (vel_max_int));
  }
  float pulses_per_degree = (float)Pulse_N / (10.0 * degrees_f);
  int current_pulse = 0;
  int recorded_degrees = 0;
  int max_timestamps = floor(degrees_f * 10.0);
  unsigned long timestamps[max_timestamps];
  float const_a = (float)vel_max_int * sqrt((float)pulse_ramp);

  Serial.print("t,");
  Serial.print(ang_abs);
  Serial.print(",");
  Serial.println( micros());

  unsigned long tempoAnterior = micros();

  // 1. RAMPA DE ACELERAÇÃO
  for (int i = 0; i < pulse_ramp; i++) {
    Pulse();
    // Verifica se alcançou o próximo grau
    current_pulse++;
    if (current_pulse >= (recorded_degrees + 1) * pulses_per_degree) {
      if (recorded_degrees < max_timestamps) {
        timestamps[recorded_degrees] = micros(); // Salva o tempo atual
        recorded_degrees++;
      }
    }
    unsigned long time_p = const_a / sqrt((float)(i + 1));// O tempo que este passo deve durar
    while (micros() - tempoAnterior < time_p) { // ESPERA DE ALTA PRECISÃO
      // Aguarda
    }
    tempoAnterior = micros(); // Zera o cronômetro
  }

  // 2. VELOCIDADE CONSTANTE
  for (int i = 0; i < (Pulse_N - (2 * pulse_ramp)); i++) {
    Pulse();
    // Verifica se alcançou o próximo grau
    current_pulse++;
    if (current_pulse >= (recorded_degrees + 1) * pulses_per_degree) {
      if (recorded_degrees < max_timestamps) {
        timestamps[recorded_degrees] = micros(); // Salva o tempo atual
        recorded_degrees++;
      }
    }
    while (micros() - tempoAnterior < vel_max_int) {
      // Aguarda
    }
    tempoAnterior = micros(); // Zera o cronômetro
  }

  // 3. RAMPA DE DESACELERAÇÃO
  for (int i = pulse_ramp - 1; i >= 0 ; i--) {
    Pulse();
    // Verifica se alcançou o próximo grau
    current_pulse++;
    if (current_pulse >= (recorded_degrees + 1) * pulses_per_degree) {
      if (recorded_degrees < max_timestamps) {
        timestamps[recorded_degrees] = micros(); // Salva o tempo atual
        recorded_degrees++;
      }
    }
    unsigned long time_p = const_a / sqrt((float)(i + 1));// O tempo que este passo deve durar
    while (micros() - tempoAnterior < time_p) {
      // Aguarda
    }
    tempoAnterior = micros(); // Zera o cronômetro
  }
  for (int i = 0; i < max_timestamps; i++) {
    Serial.print("t,");
    if (direction == 0) {
      ang_abs = ang_abs + (1.0 / 10.0);
      Serial.print(ang_abs);
    } else {
      ang_abs = ang_abs - (1.0 / 10.0);
      Serial.print(ang_abs);
    }
    Serial.print(",");
    Serial.println(timestamps[i]);
  }

}


void Homing() {
  const int max_Hsteps = 25600;
  int H_steps = 0;
  bool s1 = digitalRead(encSignal1);
  bool s2 = digitalRead(encSignal2);
  bool veio_da_direita = false;

  if (s1 && !s2) {
    SET_DIR_CCW();
    veio_da_direita = true; // Registra que o movimento inicial é pela direita
  }
  else if (s2 && !s1) {
    SET_DIR_CW();

  }
  else if (!s2 && !s1) {
    Serial.println("E,Fora da zona de homing.");
    return; // Sai da função para evitar movimentos indefinidos
  }
  delayMicroseconds(50);

  // --- FASE 1: Busca inicial até ambos os sensores ativarem ---
  while (!(digitalRead(encSignal1) && digitalRead(encSignal2)) && (H_steps < max_Hsteps)) {
    Pulse();
    H_steps++;
    delayMicroseconds(500);
  }

  // Verificação de falha da Fase 1
  if (H_steps >= max_Hsteps) {
    Serial.println("E,Limite de passos atingido no primeiro homing.");
    return;
  }

  // --- FASE 2: Inversão de marcha (Homing pela esquerda) ---
  if (veio_da_direita) {
    SET_DIR_CCW(); // Altera a direção para a esquerda
    delayMicroseconds(50);

    int H_steps_fase2 = 0;

    // Move para a esquerda ENQUANTO o sensor da direita (s2) ainda estiver ativo.
    // Ele vai parar assim que sair da zona comum e o "outro sensor" (s1) ficar sozinho.
    while (digitalRead(encSignal1) && (H_steps_fase2 < max_Hsteps)) {
      Pulse();
      H_steps_fase2++;
      delayMicroseconds(1000); //delay para aumenta a precisão do stop
    }

    // Verificação de falha da Fase 2
    if (H_steps_fase2 >= max_Hsteps) {
      Serial.println("E,Limite de passos atingido ao buscar o outro sensor.");
      return;
    }
  }
  ang_abs = 0;
}
