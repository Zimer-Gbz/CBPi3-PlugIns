import time
from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
from modules import cbpi

@cbpi.step
class ActivateActorOnTripleTempMatch(StepBase):
    step_name = Property.Text("Nome do Atuador", configurable=True, default_value="Atuador Triple Temp",
                              description="Nome para identificar este atuador no sistema")
    sensor1 = StepProperty.Sensor("Sensor 1", description="Primeiro sensor de temperatura")
    sensor2 = StepProperty.Sensor("Sensor 2", description="Segundo sensor de temperatura")
    sensor3 = StepProperty.Sensor("Sensor 3", description="Terceiro sensor de temperatura")
    actor_to_activate = StepProperty.Actor("Atuador", description="Atuador que será ativado")
    activation_time = Property.Number("Tempo de ativação (segundos)", configurable=True, default_value=30,
                                      description="Tempo que o atuador ficará ligado")
    tolerance = Property.Number("Tolerância (°C)", configurable=True, default_value=0.5,
                               description="Margem de erro para considerar temperaturas iguais")

    def init(self):
        self.timer_started = False
        self.activation_start_time = 0
        self.actor_off(self.actor_to_activate)

    def execute(self):
        temp1 = self.get_sensor_temp(self.sensor1)
        temp2 = self.get_sensor_temp(self.sensor2)
        temp3 = self.get_sensor_temp(self.sensor3)

        if None not in (temp1, temp2, temp3):
            if (abs(temp1 - temp2) <= self.tolerance and
                abs(temp2 - temp3) <= self.tolerance and
                abs(temp1 - temp3) <= self.tolerance):

                if not self.timer_started:
                    self.actor_on(self.actor_to_activate)
                    self.activation_start_time = time.time()
                    self.timer_started = True
                    self.notify("Ativação", f"{self.step_name} ativado pois 3 sensores estão com temperatura ~{temp1:.1f}°C", timeout=5000)
            else:
                if self.timer_started:
                    self.actor_off(self.actor_to_activate)
                    self.timer_started = False
                    self.notify("Desativação", f"{self.step_name} desligado: Temperaturas não coincidem mais.", timeout=3000)
        else:
            if self.timer_started:
                self.actor_off(self.actor_to_activate)
                self.timer_started = False
                self.notify("Erro", f"{self.step_name} desligado: Um ou mais sensores indisponíveis.", timeout=3000)

        if self.timer_started:
            elapsed = time.time() - self.activation_start_time
            if elapsed >= self.activation_time:
                self.actor_off(self.actor_to_activate)
                self.timer_started = False
                self.notify("Tempo encerrado", f"Tempo de ativação do {self.step_name} finalizado", timeout=3000)

    def reset(self):
        self.actor_off(self.actor_to_activate)
        self.timer_started = False
        self.activation_start_time = 0

    def finish(self):
        self.actor_off(self.actor_to_activate)
        self.timer_started = False
        self.activation_start_time = 0
