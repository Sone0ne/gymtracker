import flet as ft

from db_logic import (date_now, get_trainings, get_repeats, get_tasks, get_types_body, get_exercises_names,
                      create_repeat, create_training)
from formats import text_to_date
from create_db import init_db
from states_files import is_training_active, set_training_active

init_db()

def main(page: ft.Page):
    page.title = "Gym Tracker"
    page.window.width = 410
    page.window.height = 720
    page.window.resizable = False

    def clear_content():
        content_elements.controls.clear()
        content_elements.update()

    def disable_button(num_btn=0):
        for button in buttons_menu:
            button.disabled = False
        if num_btn != 0:
            buttons_menu[int(num_btn) - 1].disabled = True
        page.update()

    def tasks_view():
        clear_content()
        name_page_text.value = "Задачи"
        tasks = []
        for task in get_tasks():
            tasks.append(CardTask(*task))
        content_elements.controls = tasks
        disable_button(1)

    def trainings_view():
        clear_content()
        name_page_text.value = "Тренировки"
        trainings = []
        for training in get_trainings():
            trainings.append(CardTraining(*training))
        content_elements.controls = trainings
        disable_button(2)

    def profile_view():
        clear_content()
        name_page_text.value = "Профиль"
        disable_button(3)

    def statistic_view():
        clear_content()
        name_page_text.value = "Статистика"
        disable_button(4)

    def training_view(id_training):
        clear_content()
        name_page_text.value = "Тренировка"
        repeats = []
        for repeat in get_repeats(1, id_training):
            repeats.append(CardRepeat(*repeat))
        content_elements.controls = repeats
        disable_button()

    def training_now_view():
        if not is_training_active():
            set_training_active(False)

        def write_repeat():
            training_now_id = len(get_trainings())
            create_repeat(weight_field.value, counts_field.value, '1:0.0', picker_type.selected_index + 1, training_now_id)
            weight_field.value = None
            counts_field.value = None

        def stop_training():
            set_training_active(False)
            training_now_view()

        def start_training():
            if not is_training_active():
                create_training(picker_type.selected_index + 1)
                set_training_active(True)

            stage_text.value = "Выберите упражнение"
            name_page_text.value = "Тренировка"
            start_stop_button.on_click = stop_training
            start_stop_button.content = "Конец"

            picker_type.controls = exercises_names

            content_elements.controls.append(
                ft.Stack(
                    controls=[
                        ft.Stack(
                            controls=[
                                weight_field,
                                ft.Text("/", weight=ft.FontWeight.W_100, size=45, left=83, top=7, bottom=10, color=ft.Colors.LIGHT_BLUE_100),
                                counts_field,
                                repeat_button],
                            left=10, right=10,
                            top=10, bottom=10,
                        ),
                    ]
                )
            )
            page.update()

        clear_content()
        name_page_text.value = "Тренировка"
        list_body_type = [ft.Text(*t, size=15, weight=ft.FontWeight.W_600) for t in get_types_body()]
        exercises_names = [ft.Text(*t, size=15, weight=ft.FontWeight.W_600) for t in get_exercises_names()]

        picker_type = ft.CupertinoPicker(
            selected_index=0,
            item_extent=25,
            width=200,
            magnification=1.5,
            squeeze=1.2,
            use_magnifier=True,
            looping=True,
            controls=list_body_type,
        )
        weight_field = ft.TextField(label="Вес", width=60, left=5, top=20, bottom=10, border_radius=15, border_color=ft.Colors.LIGHT_BLUE_100)
        counts_field = ft.TextField(label="Раз", width=60, left=115, top=20, bottom=10, border_radius=15, border_color=ft.Colors.LIGHT_BLUE_100)

        start_stop_button = ft.Button(content="Начать",
                                 on_click=start_training,
                                width=100, height=40,
                                right=10, top=10, bottom=5)

        repeat_button = ft.Button(content="Повтор",
                                  on_click=write_repeat,
                                width=150, height=70,
                                right=0, top=10)
        information.controls.append(start_stop_button)

        stage_text = ft.Text(value="Выберите тип тренировки", weight=ft.FontWeight.W_600,
                            size=20, left=30, right=10, top=5, bottom=5)
        title_training = ft.Card(content=ft.Stack(
            controls=[stage_text]),
            left=25, right=25, top=20, width=350, height=50)

        content_elements.controls = [
            ft.Stack(
                controls=[title_training],
                height=90,
            ),
            ft.Stack(
                controls=[picker_type],
                height=80, width=400
            ),
        ]
        if is_training_active():
            start_training()
        disable_button(5)

    class CardRepeat(ft.Card):
        def __init__(self, title: str,
                     weight: int, count: int,
                     time: str, id_repeat: int, type_exercise: str, type_body: str):
            super().__init__(
                margin=5,
                content=ft.Stack(
                    controls=[
                        ft.ListTile(
                            on_click=self.open_repeat,
                            data=id_repeat,
                            title=ft.Text(f"{title.upper()}", weight=ft.FontWeight.W_600),
                            subtitle=ft.Text(f"{weight}/{count}"),
                            leading=ft.Icon(ft.Icons.CAKE),
                            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT)),
                        ft.Text(
                            value=f'{type_exercise}({type_body})',
                            top=20, right=50, size=12, weight=ft.FontWeight.W_600),
                        ft.Icon(icon=ft.Icons.TIMER, size=15, bottom=10, left=130,),
                        ft.Text(
                            value=f'{time}',
                            bottom=10, left=150, size=12, weight=ft.FontWeight.W_100),
                    ]
                )
            )

        def open_repeat(self):
            pass

    class CardTraining(ft.Card):
        def __init__(self, id_training: int, date: str, type_body: str):
            super().__init__(
                margin=7,
                content=ft.Stack(
                    controls=[
                        ft.ListTile(
                            data=id_training,
                            on_click=lambda: training_view(id_training),
                            title=ft.Text(type_body, weight=ft.FontWeight.W_600),
                            subtitle=ft.Text(f"{date}"),
                            leading=ft.Icon(ft.Icons.CIRCLE_NOTIFICATIONS),
                            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT)),
                        ft.Text(value='TEXT',
                                top=20, right=50, size=12, weight=ft.FontWeight.W_600),

                    ]
                )
            )

    class CardTask(ft.Card):
        def __init__(self, id_task: int, title: str,
                     weight: int, count: int,
                     date_need: str, create_date: str, complete_date: str,
                     type_exercise: str, type_body: str):
            super().__init__(
                margin=7,
                content=ft.Stack(
                    controls=[
                        ft.ListTile(
                            data=id_task,
                            on_click=self.open_task,
                            title=ft.Text(f"{title.upper()}", weight=ft.FontWeight.W_600),
                            subtitle=ft.Text(f"{weight}/{count}"),
                            leading=ft.Icon(ft.Icons.CIRCLE_NOTIFICATIONS),
                            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT)),
                        ft.Text(value=f'{self.calculate_days(date_now, date_need)} дней' if complete_date is None else 'Выполнено',
                                top=2, right=50, size=11, weight=ft.FontWeight.W_900),
                        ft.Text(value=f'{type_exercise}({type_body})',
                                top=20, right=50, size=12, weight=ft.FontWeight.W_600),

                    ]
                )
            )

        def open_task(self):
            pass

        @classmethod
        def calculate_days(self, date_first, date_need):
            return (text_to_date(date_need) - date_first).days

    class MenuButton(ft.CupertinoButton):
        def __init__(self, icon: ft.Icon, on_click, data: str):
            super().__init__(
                width=65,
                expand=True,
                data=data,
                disabled=False,
                icon=icon,
                on_click=on_click
            )

    probel = ft.Container(width=15)
    name_page_text = ft.Text(
        value="",
        width=250,
        weight=ft.FontWeight.W_600,
        size=24
    )

    info_row = ft.Row(controls=[probel, name_page_text])

    information = ft.Stack(
        controls=[info_row],
        width=400,
        height=50,
    )

    content_elements = ft.Column(
        margin=0,
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        controls=[],
    )

    elements = ft.Container(
        width=400,
        height=530,
        margin=1,
        bgcolor=ft.Colors.BLACK_26,
        border_radius=16,
        content=content_elements
        )

    buttons_menu = [
        MenuButton(data="1",
                   icon=ft.Icon(ft.Icons.TASK_ALT),
                   on_click=tasks_view),
        MenuButton(data="2",
                   icon=ft.Icon(ft.Icons.NOTES_OUTLINED),
                   on_click=trainings_view),
        MenuButton(data="3",
                   icon=ft.Icon(ft.Icons.PERSON),
                   on_click=profile_view),
        MenuButton(data="4",
                   icon=ft.Icon(ft.Icons.LEADERBOARD_SHARP),
                   on_click=statistic_view),
        MenuButton(data="5",
                   icon=ft.Icon(ft.Icons.ADD),
                   on_click=training_now_view),
        ]
    menu = ft.Container(width=400,
                        height=60,
                        border_radius=15,
                        alignment=ft.Alignment.CENTER,
                        bgcolor=ft.Colors.BLACK_26,
                        content=ft.Row(controls=buttons_menu, spacing=5)
                        )

    page.add(information, elements, menu)

if __name__ == "__main__":
    ft.run(main)
