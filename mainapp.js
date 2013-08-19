var main = angular.module('main', []);

main.run(function($templateCache) {
    var templates = document.getElementsByTagName('template');
    angular.forEach(templates, function(tmpl) {
        $templateCache.put(tmpl.getAttribute('name'), tmpl.innerHTML);
    })
});

main.controller('CarouselCtrl', function($scope, $timeout, $templateCache) {
    $scope.showing = {
        ability: '',
        content: '',
    }
    $scope.slides = [
        'staticweb-server',
        'irc-server',
        'run-trial',
    ];
    $scope.index = 0;

    $scope.next = function() {
        $scope.index += 1;
        if ($scope.index >= $scope.slides.length) {
            $scope.index = 0;
        }
    }
    $scope.prev = function() {
        $scope.index -= 1;
        if ($scope.index < 0) {
            $scope.index = $scope.slides.length-1;
        }
    }

    $scope.$watch('index', function() {
        var slide = $scope.slides[$scope.index];
        $scope.showing.ability = $templateCache.get(slide + '.title');
        $scope.showing.content = $templateCache.get(slide + '.html');
    })

    $scope.fuse = function() {
        $timeout(function() {
            $scope.next();
        }, 5000).then(function() {
            $scope.fuse();
        });
    }
    $scope.fuse();
})